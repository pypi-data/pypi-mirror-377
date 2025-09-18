import anywidget
import traitlets

class Widget(anywidget.AnyWidget):
    _esm = """
    import * as d3 from "https://cdn.skypack.dev/d3@7";
    
    let RDKit = null;
    
    async function render({ model, el }) {
        // Initialize RDKit if not already done
        if (!RDKit) {
            try {
                // Load RDKit from jsdelivr CDN
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/@rdkit/rdkit/dist/RDKit_minimal.js';
                document.head.appendChild(script);
                
                await new Promise((resolve, reject) => {
                    script.onload = async () => {
                        try {
                            RDKit = await window.initRDKitModule();
                            console.log("RDKit loaded successfully");
                            resolve();
                        } catch (e) {
                            reject(e);
                        }
                    };
                    script.onerror = reject;
                });
            } catch (error) {
                console.warn("RDKit not available, SMILES rendering disabled:", error);
            }
        }
        
        // Clear previous content
        el.innerHTML = '';
        
        // Create container
        const container = d3.select(el)
            .style("width", "100%")
            .style("height", "300px");
        
        // Create bordered wrapper
        const borderedWrapper = container.append("div")
            .style("border", "2px solid #2d5a2d")
            .style("border-radius", "10px")
            .style("padding", "15px")
            .style("background-color", "white")
            .style("width", "fit-content")
            .style("margin", "0 auto");
        
        // Create layout container
        const layoutContainer = borderedWrapper.append("div")
            .style("display", "flex")
            .style("align-items", "flex-start");
        
        // Create SVG container
        const svgContainer = layoutContainer.append("div");
        
        // Create SVG
        const margin = {top: 20, right: 30, bottom: 50, left: 50};
        const width = 500 - margin.left - margin.right;
        const height = 260 - margin.top - margin.bottom;
        
        const svg = svgContainer.append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);
        
        // Create box container to the right
        const boxContainer = layoutContainer.append("div")
            .style("width", "500px")
            .style("height", (height + margin.top + margin.bottom - 50) + "px") // Reduced height to make room for button
            .style("margin-left", "20px")
            .style("display", "flex")
            .style("flex-direction", "column");
        
        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);
        
        // Function to render SMILES as image
        function renderSMILES(smiles, container, molName = null) {
            console.log("renderSMILES called with:", molName, smiles.substring(0, 20) + "...");
            
            // Clear container properly
            const containerNode = container.node ? container.node() : container;
            if (containerNode) {
                containerNode.innerHTML = '';
                console.log("Container cleared successfully");
            } else {
                console.error("Could not get container node");
            }
            
            // Create molecule display container (flex-grow to take available space)
            const moleculeContainer = container.append("div")
                .style("flex-grow", "1")
                .style("display", "flex")
                .style("align-items", "center")
                .style("justify-content", "center")
                .style("text-align", "center");
            
            // Create button container (fixed height at bottom)
            const buttonContainer = container.append("div")
                .style("flex-shrink", "0")
                .style("text-align", "center")
                .style("padding-top", "10px");
            
            if (!RDKit || !smiles) {
                // Fallback: display SMILES as text
                const fallbackDiv = moleculeContainer.append("div")
                    .style("padding", "15px")
                    .style("text-align", "center");
                
                if (molName) {
                    fallbackDiv.append("div")
                        .style("font-weight", "bold")
                        .style("margin-bottom", "10px")
                        .style("color", "#333")
                        .text(molName);
                }
                
                fallbackDiv.append("div")
                    .style("font-family", "monospace")
                    .style("font-size", "12px")
                    .style("color", "#666")
                    .style("word-break", "break-all")
                    .style("line-height", "1.4")
                    .text(smiles || "No SMILES available");
                
            } else {
                try {
                    const mol = RDKit.get_mol(smiles);
                    if (mol) {
                        const svg_text = mol.get_svg(450, 200); // Reduced height to make room for button
                        const moleculeNode = moleculeContainer.node();
                        if (moleculeNode) {
                            moleculeNode.innerHTML = svg_text;
                        }
                        mol.delete();
                    } else {
                        // Fallback for invalid SMILES
                        const fallbackDiv = moleculeContainer.append("div")
                            .style("padding", "15px")
                            .style("text-align", "center");
                        
                        if (molName) {
                            fallbackDiv.append("div")
                                .style("font-weight", "bold")
                                .style("margin-bottom", "10px")
                                .style("color", "#333")
                                .text(molName);
                        }
                        
                        fallbackDiv.append("div")
                            .style("color", "#666")
                            .text("Invalid SMILES");
                        
                        fallbackDiv.append("div")
                            .style("font-family", "monospace")
                            .style("font-size", "12px")
                            .style("color", "#999")
                            .style("margin-top", "5px")
                            .text(smiles);
                    }
                } catch (error) {
                    console.error("Error rendering SMILES:", error);
                    // Fallback for render error
                    const fallbackDiv = moleculeContainer.append("div")
                        .style("padding", "15px")
                        .style("text-align", "center");
                    
                    if (molName) {
                        fallbackDiv.append("div")
                            .style("font-weight", "bold")
                            .style("margin-bottom", "10px")
                            .style("color", "#333")
                            .text(molName);
                    }
                    
                    fallbackDiv.append("div")
                        .style("color", "#666")
                        .text("Error rendering molecule");
                    
                    fallbackDiv.append("div")
                        .style("font-family", "monospace")
                        .style("font-size", "12px")
                        .style("color", "#999")
                        .style("margin-top", "5px")
                        .text(smiles);
                }
            }
            
            // Add Copy SMILES button if SMILES is available
            if (smiles) {
                const copyButton = buttonContainer.append("button")
                    .style("padding", "8px 16px")
                    .style("background-color", "#2d5a2d")
                    .style("color", "white")
                    .style("border", "none")
                    .style("border-radius", "5px")
                    .style("cursor", "pointer")
                    .style("font-size", "14px")
                    .style("font-weight", "500")
                    .text("Copy SMILES")
                    .on("click", function() {
                        // Copy SMILES to clipboard
                        navigator.clipboard.writeText(smiles).then(() => {
                            // Visual feedback - change button text temporarily
                            d3.select(this)
                                .text("Copied!")
                                .style("background-color", "#4a8a4a");
                            
                            setTimeout(() => {
                                d3.select(this)
                                    .text("Copy SMILES")
                                    .style("background-color", "#2d5a2d");
                            }, 1500);
                        }).catch(err => {
                            console.error('Failed to copy SMILES: ', err);
                            // Fallback - show alert with SMILES
                            alert('Copy failed. SMILES: ' + smiles);
                        });
                    })
                    .on("mouseover", function() {
                        d3.select(this).style("background-color", "#1e3e1e");
                    })
                    .on("mouseout", function() {
                        d3.select(this).style("background-color", "#2d5a2d");
                    });
            }
        }
        
        function updatePlot() {
            const data = JSON.parse(model.get("data"));
            
            // Clear previous plot
            g.selectAll("*").remove();
            
            // Render SMILES from first row in the box
            if (data.length > 0) {
                const firstRow = data[0];
                renderSMILES(firstRow.smiles, boxContainer, firstRow.name);
            }
            
            
            // Group by smiles
            const groupedBySmiles = d3.group(data, d => d.smiles);
            
            // Set up scales
            const xExtent = d3.extent(data, d => d.pH);
            const yExtent = d3.extent(data, d => d.population);
            
            const xScale = d3.scaleLinear()
                .domain(xExtent)
                .range([0, width]);
            
            const yScale = d3.scaleLinear()
                .domain([0, yExtent[1]])
                .range([height, 0]);
            
            // Color scale
            const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
            const smilesArray = Array.from(groupedBySmiles.keys());
            
            // Line generator
            const line = d3.line()
                .x(d => xScale(d.pH))
                .y(d => yScale(d.population))
                .curve(d3.curveMonotoneX);
            
            // Create lines for each SMILES
            let groupIndex = 0;
            groupedBySmiles.forEach((values, smiles) => {
                // Sort by pH for proper line drawing
                const sortedValues = values.sort((a, b) => a.pH - b.pH);
                const currentGroupIndex = groupIndex++; // Unique index for this group
                
                g.append("path")
                    .datum(sortedValues)
                    .attr("fill", "none")
                    .attr("stroke", colorScale(smiles))
                    .attr("stroke-width", 2)
                    .attr("d", line)
                    .attr("data-smiles", smiles)
                    .attr("data-group-index", currentGroupIndex)
                    .on("mouseover", function(event) {
                        // Highlight line
                        d3.select(this).attr("stroke-width", 4);
                        
                        // Show tooltip
                        const tooltip = d3.select("body").append("div")
                            .attr("class", "tooltip")
                            .style("position", "absolute")
                            .style("background", "black")
                            .style("color", "white")
                            .style("padding", "5px")
                            .style("border-radius", "3px")
                            .style("pointer-events", "none");
                        
                        // Get the first data point to show name
                        const firstPoint = sortedValues[0];
                        tooltip.html(`${firstPoint.name}<br>pH: ${firstPoint.pH.toFixed(2)}<br>Population: ${firstPoint.population.toFixed(4)}<br>SMILES: ${smiles}`)
                            .style('font-size', '12px')
                            .style("left", (event.pageX + 10) + "px")
                            .style("top", (event.pageY - 10) + "px");
                    })
                    .on("mouseout", function() {
                        // Restore line width
                        d3.select(this).attr("stroke-width", 2);
                        d3.selectAll(".tooltip").remove();
                    });
                
                // Add invisible clickable points
                g.selectAll(`.point-group-${currentGroupIndex}`)
                    .data(sortedValues)
                    .enter()
                    .append("circle")
                    .attr("class", `point-group-${currentGroupIndex}`)
                    .attr("cx", d => xScale(d.pH))
                    .attr("cy", d => yScale(d.population))
                    .attr("r", 4)
                    .attr("fill", "transparent")
                    .style("cursor", "pointer")
                    .on("mouseover", function(event, d) {
                        // Show detailed tooltip
                        const tooltip = d3.select("body").append("div")
                            .attr("class", "tooltip")
                            .style("position", "absolute")
                            .style("background", "black")
                            .style("color", "white")
                            .style("padding", "5px")
                            .style("border-radius", "3px")
                            .style("pointer-events", "none");
                        
                        tooltip.html(`${d.name}<br>pH: ${d.pH.toFixed(2)}<br>Population: ${d.population.toFixed(4)}<br>SMILES: ${d.smiles}<br><em>Click to view molecule</em>`)
                            .style("left", (event.pageX + 10) + "px")
                            .style("top", (event.pageY - 10) + "px")
                            .style('font-size', '12px');
                        
                        // Highlight the corresponding line
                        d3.select(`path[data-group-index="${currentGroupIndex}"]`)
                            .attr("stroke-width", 4);
                    })
                    .on("mouseout", function() {
                        d3.selectAll(".tooltip").remove();
                        
                        // Restore line width
                        d3.select(`path[data-group-index="${currentGroupIndex}"]`)
                            .attr("stroke-width", 2);
                    })
                    .on("click", function(event, d) {
                        console.log("Clicked on point:", d.name, "SMILES:", d.smiles.substring(0, 20) + "...");
                        
                        // Update SMILES display in box - use the boxContainer directly
                        renderSMILES(d.smiles, boxContainer, d.name);
                        
                        // Visual feedback - briefly highlight the line
                        d3.select(`path[data-group-index="${currentGroupIndex}"]`)
                            .transition()
                            .duration(200)
                            .attr("stroke-width", 6)
                            .transition()
                            .duration(200)
                            .attr("stroke-width", 2);
                    });
            });
            
            // Add x-axis
            g.append("g")
                .attr("transform", `translate(0,${height})`)
                .call(d3.axisBottom(xScale));
            
            // Add y-axis
            g.append("g")
                .call(d3.axisLeft(yScale));
            
            // Add labels
            g.append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 0 - margin.left)
                .attr("x", 0 - (height / 2))
                .attr("dy", "1em")
                .style("text-anchor", "middle")
                .text("Population");
            
            g.append("text")
                .attr("transform", `translate(${width/2}, ${height + margin.bottom})`)
                .style("text-anchor", "middle")
                .text("pH");
            
        }
        
        // Initial plot
        updatePlot();
        
        // Update plot when data changes
        model.on("change:data", updatePlot);
    }
    
    export default { render };
    """
    
    # Traitlets for data
    data = traitlets.Unicode("[]").tag(sync=True)
    
    def __init__(self, df, **kwargs):
        super().__init__(**kwargs)
        self.df = df
        self.update_data()
    
    def update_data(self):
        """Convert DataFrame to JSON for JavaScript"""
        # Convert DataFrame to list of dictionaries
        data_list = self.df.to_dict('records')
        import json
        self.data = json.dumps(data_list)
