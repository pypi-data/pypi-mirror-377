import argparse
import logging

import torch
from torch import nn

from ..dict import DICT, DICT_CHARGE, Dictionary
from .transformer import TransformerEncoderWithPair, get_activation_fn

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

torch.serialization.add_safe_globals([argparse.Namespace])

BACKBONE = {
    "transformer": TransformerEncoderWithPair,
}


class UniMolModel(nn.Module):
    """
    UniMolModel is a specialized model for molecular, protein, crystal, or MOF (Metal-Organic Frameworks) data.
    It dynamically configures its architecture based on the type of data it is intended to work with. The model
    supports multiple data types and incorporates various architecture configurations and pretrained weights.

    Attributes:
        - output_dim: The dimension of the output layer.
        - data_type: The type of data the model is designed to handle.
        - remove_hs: Flag to indicate whether hydrogen atoms are removed in molecular data.
        - pretrain_path: Path to the pretrained model weights.
        - dictionary: The dictionary object used for tokenization and encoding.
        - mask_idx: Index of the mask token in the dictionary.
        - padding_idx: Index of the padding token in the dictionary.
        - embed_tokens: Embedding layer for token embeddings.
        - encoder: Transformer encoder backbone of the model.
        - gbf_proj, gbf: Layers for Gaussian basis functions or numerical embeddings.
        - classification_head: The final classification head of the model.
    """

    def __init__(self, model_path, output_dim=2, **params):
        """
        Initializes the UniMolModel with specified parameters and data type.

        :param output_dim: (int) The number of output dimensions (classes).
        :param data_type: (str) The type of data (e.g., 'molecule', 'protein').
        :param params: Additional parameters for model configuration.
        """
        super().__init__()
        self.args = molecule_architecture()
        self.output_dim = output_dim
        self.remove_hs = params.get("remove_hs", False)
        self.pretrain_path = model_path
        self.head_name = params.get("head_name", "chembl_all")
        self.dict_dir = params.get("dict_dir", "dict")
        self.dictionary = Dictionary.load_from_str(DICT)
        self.mask_idx = self.dictionary.add_symbol("[MASK]", is_special=True)
        self.padding_idx = self.dictionary.pad()
        self.embed_tokens = nn.Embedding(len(self.dictionary), self.args.encoder_embed_dim, self.padding_idx)
        self.charge_dictionary = Dictionary.load_from_str(DICT_CHARGE)
        self.charge_mask_idx = self.charge_dictionary.add_symbol("[MASK]", is_special=True)
        self.charge_padding_idx = self.charge_dictionary.pad()
        self.embed_charges = nn.Embedding(
            len(self.charge_dictionary), self.args.encoder_embed_dim, self.charge_padding_idx
        )
        self.encoder = BACKBONE[self.args.backbone](
            encoder_layers=self.args.encoder_layers,
            embed_dim=self.args.encoder_embed_dim,
            ffn_embed_dim=self.args.encoder_ffn_embed_dim,
            attention_heads=self.args.encoder_attention_heads,
            emb_dropout=self.args.emb_dropout,
            dropout=self.args.dropout,
            attention_dropout=self.args.attention_dropout,
            activation_dropout=self.args.activation_dropout,
            max_seq_len=self.args.max_seq_len,
            activation_fn=self.args.activation_fn,
            no_final_head_layer_norm=self.args.delta_pair_repr_norm_loss < 0,
        )
        K = 128
        n_edge_type = len(self.dictionary) * len(self.dictionary)
        self.gbf_proj = NonLinearHead(K, self.args.encoder_attention_heads, self.args.activation_fn)
        if self.args.kernel == "gaussian":
            self.gbf = GaussianLayer(K, n_edge_type)
        self.classification_heads = nn.ModuleDict()
        self.classification_heads[self.head_name] = ClassificationHead(
            input_dim=self.args.encoder_embed_dim,
            inner_dim=self.args.encoder_embed_dim,
            num_classes=self.output_dim,
            activation_fn=self.args.pooler_activation_fn,
            pooler_dropout=self.args.pooler_dropout,
        )
        self.load_pretrained_weights(path=self.pretrain_path)

    def load_pretrained_weights(self, path):
        """
        Loads pretrained weights into the model.

        :param path: (str) Path to the pretrained weight file.
        """
        if path is not None:
            logger.debug("Loading pretrained weights from {}".format(path))
            state_dict = torch.load(path, weights_only=False, map_location=lambda storage, loc: storage)
            errors = self.load_state_dict(state_dict["model"], strict=True)
            if errors.missing_keys:
                logger.warning("Error in loading model state, missing_keys " + str(errors.missing_keys))
            if errors.unexpected_keys:
                logger.warning("Error in loading model state, unexpected_keys " + str(errors.unexpected_keys))

    @classmethod
    def build_model(cls, args):
        """
        Class method to build a new instance of the UniMolModel.

        :param args: Arguments for model configuration.
        :return: An instance of UniMolModel.
        """
        return cls(args)

    def forward(
        self,
        src_tokens,
        src_charges,
        src_distance,
        src_coord,
        src_edge_type,
        return_repr=False,
        return_atomic_reprs=False,
        **kwargs,
    ):
        """
        Defines the forward pass of the model.

        :param src_tokens: Tokenized input data.
        :param src_distance: Additional molecular features.
        :param src_coord: Additional molecular features.
        :param src_edge_type: Additional molecular features.
        :param gas_id: Optional environmental features for MOFs.
        :param gas_attr: Optional environmental features for MOFs.
        :param pressure: Optional environmental features for MOFs.
        :param temperature: Optional environmental features for MOFs.
        :param return_repr: Flags to return intermediate representations.
        :param return_atomic_reprs: Flags to return intermediate representations.

        :return: Output logits or requested intermediate representations.
        """
        padding_mask = src_tokens.eq(self.padding_idx)
        if not padding_mask.any():
            padding_mask = None
        x = self.embed_tokens(src_tokens)
        # involve charge info
        charge_padding_mask = src_charges.eq(self.charge_padding_idx)
        if not charge_padding_mask.any():
            padding_mask = None
        charges_emb = self.embed_charges(src_charges)
        x += charges_emb

        def get_dist_features(dist, et):
            n_node = dist.size(-1)
            gbf_feature = self.gbf(dist, et)
            gbf_result = self.gbf_proj(gbf_feature)
            graph_attn_bias = gbf_result
            graph_attn_bias = graph_attn_bias.permute(0, 3, 1, 2).contiguous()
            graph_attn_bias = graph_attn_bias.view(-1, n_node, n_node)
            return graph_attn_bias

        graph_attn_bias = get_dist_features(src_distance, src_edge_type)
        (
            encoder_rep,
            _,
            _,
            _,
            _,
        ) = self.encoder(x, padding_mask=padding_mask, attn_mask=graph_attn_bias)
        cls_repr = encoder_rep[:, 0, :]  # CLS token repr
        all_repr = encoder_rep[:, :, :]  # all token repr

        filtered_tensors = []
        filtered_coords = []
        for tokens, coord in zip(src_tokens, src_coord):
            filtered_tensor = tokens[(tokens != 0) & (tokens != 1) & (tokens != 2)]  # filter out BOS(0), EOS(1), PAD(2)
            filtered_coord = coord[(tokens != 0) & (tokens != 1) & (tokens != 2)]
            filtered_tensors.append(filtered_tensor)
            filtered_coords.append(filtered_coord)

        lengths = [
            len(filtered_tensor) for filtered_tensor in filtered_tensors
        ]  # Compute the lengths of the filtered tensors
        if return_repr and return_atomic_reprs:
            cls_atomic_reprs = []
            atomic_symbols = []
            for i in range(len(all_repr)):
                atomic_reprs = encoder_rep[i, 1 : lengths[i] + 1, :]
                atomic_symbol = []
                for atomic_num in filtered_tensors[i]:
                    atomic_symbol.append(self.dictionary.symbols[atomic_num])
                atomic_symbols.append(atomic_symbol)
                cls_atomic_reprs.append(atomic_reprs)
            return {
                "cls_repr": cls_repr,
                "atomic_symbol": atomic_symbols,
                "atomic_coords": filtered_coords,
                "atomic_reprs": cls_atomic_reprs,
            }
        if return_repr and not return_atomic_reprs:
            return {"cls_repr": cls_repr}

        logits = self.classification_heads[self.head_name](cls_repr)
        return logits

    def batch_collate_fn(self, samples):
        """
        Custom collate function for batch processing non-MOF data.

        :param samples: A list of sample data.

        :return: A tuple containing a batch dictionary and labels.
        """
        batch = {}
        for k in samples[0][0].keys():
            if k == "src_coord":
                v = pad_coords([torch.tensor(s[0][k]).float() for s in samples], pad_idx=0.0)
            elif k == "src_edge_type":
                v = pad_2d([torch.tensor(s[0][k]).long() for s in samples], pad_idx=self.padding_idx)
            elif k == "src_distance":
                v = pad_2d([torch.tensor(s[0][k]).float() for s in samples], pad_idx=0.0)
            elif k == "src_tokens":
                v = pad_1d_tokens([torch.tensor(s[0][k]).long() for s in samples], pad_idx=self.padding_idx)
            elif k == "src_charges":
                v = pad_1d_tokens([torch.tensor(s[0][k]).long() for s in samples], pad_idx=self.charge_padding_idx)
            batch[k] = v
        try:
            label = torch.tensor([s[1] for s in samples])
        except Exception:
            label = None
        return batch, label


class ClassificationHead(nn.Module):
    """Head for sentence-level classification tasks."""

    def __init__(
        self,
        input_dim,
        inner_dim,
        num_classes,
        activation_fn,
        pooler_dropout,
    ):
        """
        Initialize the classification head.

        :param input_dim: Dimension of input features.
        :param inner_dim: Dimension of the inner layer.
        :param num_classes: Number of classes for classification.
        :param activation_fn: Activation function name.
        :param pooler_dropout: Dropout rate for the pooling layer.
        """
        super().__init__()
        self.dense = nn.Linear(input_dim, inner_dim)
        self.activation_fn = get_activation_fn(activation_fn)
        self.dropout = nn.Dropout(p=pooler_dropout)
        self.out_proj = nn.Linear(inner_dim, num_classes)

    def forward(self, features, **kwargs):
        """
        Forward pass for the classification head.

        :param features: Input features for classification.

        :return: Output from the classification head.
        """
        x = features
        x = self.dropout(x)
        x = self.dense(x)
        x = self.activation_fn(x)
        x = self.dropout(x)
        x = self.out_proj(x)
        return x


class NonLinearHead(nn.Module):
    """
    A neural network module used for simple classification tasks. It consists of a two-layered linear network
    with a nonlinear activation function in between.

    Attributes:
        - linear1: The first linear layer.
        - linear2: The second linear layer that outputs to the desired dimensions.
        - activation_fn: The nonlinear activation function.
    """

    def __init__(
        self,
        input_dim,
        out_dim,
        activation_fn,
        hidden=None,
    ):
        """
        Initializes the NonLinearHead module.

        :param input_dim: Dimension of the input features.
        :param out_dim: Dimension of the output.
        :param activation_fn: The activation function to use.
        :param hidden: Dimension of the hidden layer; defaults to the same as input_dim if not provided.
        """
        super().__init__()
        hidden = input_dim if not hidden else hidden
        self.linear1 = nn.Linear(input_dim, hidden)
        self.linear2 = nn.Linear(hidden, out_dim)
        self.activation_fn = get_activation_fn(activation_fn)

    def forward(self, x):
        """
        Forward pass of the NonLinearHead.

        :param x: Input tensor to the module.

        :return: Tensor after passing through the network.
        """
        x = self.linear1(x)
        x = self.activation_fn(x)
        x = self.linear2(x)
        return x


@torch.jit.script
def gaussian(x, mean, std):
    """
    Gaussian function implemented for PyTorch tensors.

    :param x: The input tensor.
    :param mean: The mean for the Gaussian function.
    :param std: The standard deviation for the Gaussian function.

    :return: The output tensor after applying the Gaussian function.
    """
    pi = 3.14159
    a = (2 * pi) ** 0.5
    return torch.exp(-0.5 * (((x - mean) / std) ** 2)) / (a * std)


class GaussianLayer(nn.Module):
    """
    A neural network module implementing a Gaussian layer, useful in graph neural networks.

    Attributes:
        - K: Number of Gaussian kernels.
        - means, stds: Embeddings for the means and standard deviations of the Gaussian kernels.
        - mul, bias: Embeddings for scaling and bias parameters.
    """

    def __init__(self, K=128, edge_types=1024):
        """
        Initializes the GaussianLayer module.

        :param K: Number of Gaussian kernels.
        :param edge_types: Number of different edge types to consider.

        :return: An instance of the configured Gaussian kernel and edge types.
        """
        super().__init__()
        self.K = K
        self.means = nn.Embedding(1, K)
        self.stds = nn.Embedding(1, K)
        self.mul = nn.Embedding(edge_types, 1)
        self.bias = nn.Embedding(edge_types, 1)
        nn.init.uniform_(self.means.weight, 0, 3)
        nn.init.uniform_(self.stds.weight, 0, 3)
        nn.init.constant_(self.bias.weight, 0)
        nn.init.constant_(self.mul.weight, 1)

    def forward(self, x, edge_type):
        """
        Forward pass of the GaussianLayer.

        :param x: Input tensor representing distances or other features.
        :param edge_type: Tensor indicating types of edges in the graph.

        :return: Tensor transformed by the Gaussian layer.
        """
        mul = self.mul(edge_type).type_as(x)
        bias = self.bias(edge_type).type_as(x)
        x = mul * x.unsqueeze(-1) + bias
        x = x.expand(-1, -1, -1, self.K)
        mean = self.means.weight.float().view(-1)
        std = self.stds.weight.float().view(-1).abs() + 1e-5
        return gaussian(x.float(), mean, std).type_as(self.means.weight)


def molecule_architecture():
    args = argparse.ArgumentParser()
    args.encoder_layers = getattr(args, "encoder_layers", 15)
    args.encoder_embed_dim = getattr(args, "encoder_embed_dim", 512)
    args.encoder_ffn_embed_dim = getattr(args, "encoder_ffn_embed_dim", 2048)
    args.encoder_attention_heads = getattr(args, "encoder_attention_heads", 64)
    args.dropout = getattr(args, "dropout", 0.1)
    args.emb_dropout = getattr(args, "emb_dropout", 0.1)
    args.attention_dropout = getattr(args, "attention_dropout", 0.1)
    args.activation_dropout = getattr(args, "activation_dropout", 0.0)
    args.pooler_dropout = getattr(args, "pooler_dropout", 0.0)
    args.max_seq_len = getattr(args, "max_seq_len", 512)
    args.activation_fn = getattr(args, "activation_fn", "gelu")
    args.pooler_activation_fn = getattr(args, "pooler_activation_fn", "tanh")
    args.post_ln = getattr(args, "post_ln", False)
    args.backbone = getattr(args, "backbone", "transformer")
    args.kernel = getattr(args, "kernel", "gaussian")
    args.delta_pair_repr_norm_loss = getattr(args, "delta_pair_repr_norm_loss", -1.0)
    return args


def pad_1d_tokens(
    values,
    pad_idx,
    left_pad=False,
    pad_to_length=None,
    pad_to_multiple=1,
):
    """
    padding one dimension tokens inputs.

    :param values: A list of 1d tensors.
    :param pad_idx: The padding index.
    :param left_pad: Whether to left pad the tensors. Defaults to False.
    :param pad_to_length: The desired length of the padded tensors. Defaults to None.
    :param pad_to_multiple: The multiple to pad the tensors to. Defaults to 1.

    :return: A padded 1d tensor as a torch.Tensor.

    """
    size = max(v.size(0) for v in values)
    size = size if pad_to_length is None else max(size, pad_to_length)
    if pad_to_multiple != 1 and size % pad_to_multiple != 0:
        size = int(((size - 0.1) // pad_to_multiple + 1) * pad_to_multiple)
    res = values[0].new(len(values), size).fill_(pad_idx)

    def copy_tensor(src, dst):
        assert dst.numel() == src.numel()
        dst.copy_(src)

    for i, v in enumerate(values):
        copy_tensor(v, res[i][size - len(v) :] if left_pad else res[i][: len(v)])
    return res


def pad_2d(
    values,
    pad_idx,
    left_pad=False,
    pad_to_length=None,
    pad_to_multiple=1,
):
    """
    padding two dimension tensor inputs.

    :param values: A list of 2d tensors.
    :param pad_idx: The padding index.
    :param left_pad: Whether to pad on the left side. Defaults to False.
    :param pad_to_length: The length to pad the tensors to. If None, the maximum length in the list
                         is used. Defaults to None.
    :param pad_to_multiple: The multiple to pad the tensors to. Defaults to 1.

    :return: A padded 2d tensor as a torch.Tensor.
    """
    size = max(v.size(0) for v in values)
    size = size if pad_to_length is None else max(size, pad_to_length)
    if pad_to_multiple != 1 and size % pad_to_multiple != 0:
        size = int(((size - 0.1) // pad_to_multiple + 1) * pad_to_multiple)
    res = values[0].new(len(values), size, size).fill_(pad_idx)

    def copy_tensor(src, dst):
        assert dst.numel() == src.numel()
        dst.copy_(src)

    for i, v in enumerate(values):
        copy_tensor(v, res[i][size - len(v) :, size - len(v) :] if left_pad else res[i][: len(v), : len(v)])
    return res


def pad_coords(
    values,
    pad_idx,
    left_pad=False,
    pad_to_length=None,
    pad_to_multiple=1,
):
    """
    padding two dimension tensor coords which the third dimension is 3.

    :param values: A list of 1d tensors.
    :param pad_idx: The value used for padding.
    :param left_pad: Whether to pad on the left side. Defaults to False.
    :param pad_to_length: The desired length of the padded tensor. Defaults to None.
    :param pad_to_multiple: The multiple to pad the tensor to. Defaults to 1.

    :return: A padded 2d coordinate tensor as a torch.Tensor.
    """
    size = max(v.size(0) for v in values)
    size = size if pad_to_length is None else max(size, pad_to_length)
    if pad_to_multiple != 1 and size % pad_to_multiple != 0:
        size = int(((size - 0.1) // pad_to_multiple + 1) * pad_to_multiple)
    res = values[0].new(len(values), size, 3).fill_(pad_idx)

    def copy_tensor(src, dst):
        assert dst.numel() == src.numel()
        dst.copy_(src)

    for i, v in enumerate(values):
        copy_tensor(v, res[i][size - len(v) :, :] if left_pad else res[i][: len(v), :])
    return res
