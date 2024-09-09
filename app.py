from flask import Flask, request, jsonify, render_template
import pandas as pd
import json
import traceback
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
            
            if not categorical_columns:
                return jsonify({'error': 'No categorical columns found in the CSV'}), 400
            
            # Select the first categorical column as the filter
            filter_column = categorical_columns[3]
            filter_categories = df[filter_column].unique().tolist()
            
            data = []
            for col in numeric_columns:
                for category in filter_categories:
                    subset = df[df[filter_column] == category]
                    data.append({
                        "name": col,
                        "category": category,
                        "value": subset[col].mean()
                    })
            
            d3_code = f"""
            (function() {{
                const data = {json.dumps(data)};
                const columns = {json.dumps(numeric_columns)};
                const categories = {json.dumps(filter_categories)};
                const filterColumn = "{filter_column}";
                
                const margin = {{top: 40, right: 150, bottom: 60, left: 60}};
                const width = 800 - margin.left - margin.right;
                const height = 500 - margin.top - margin.bottom;

                const svg = d3.select("#dashboard")
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

                const x = d3.scaleBand()
                    .range([0, width])
                    .padding(0.1);

                const y = d3.scaleLinear()
                    .range([height, 0]);

                const color = d3.scaleOrdinal()
                    .domain(categories)
                    .range(d3.schemeCategory10);

                x.domain(columns);
                y.domain([0, d3.max(data, d => d.value)]);

                // Add X axis
                svg.append("g")
                    .attr("transform", `translate(0,${{height}})`)
                    .call(d3.axisBottom(x))
                    .selectAll("text")
                    .attr("transform", "rotate(-45)")
                    .style("text-anchor", "end");

                // Add Y axis
                svg.append("g")
                    .call(d3.axisLeft(y));

                // Bars
                svg.selectAll(".bar")
                    .data(data)
                    .enter()
                    .append("rect")
                    .attr("class", "bar")
                    .attr("x", d => x(d.name))
                    .attr("y", d => y(d.value))
                    .attr("width", x.bandwidth() / categories.length)
                    .attr("height", d => height - y(d.value))
                    .attr("fill", d => color(d.category))
                    .attr("transform", d => `translate(${{(x.bandwidth() / categories.length) * categories.indexOf(d.category)}}, 0)`)
                    .on("mouseover", function(event, d) {{
                        d3.select(this).attr("opacity", 0.8);
                        tooltip.transition()
                            .duration(200)
                            .style("opacity", .9);
                        tooltip.html(`${{filterColumn}}: ${{d.category}}<br/>${{d.name}}: ${{d.value.toFixed(2)}}`)
                            .style("left", (event.pageX) + "px")
                            .style("top", (event.pageY - 28) + "px");
                    }})
                    .on("mouseout", function(d) {{
                        d3.select(this).attr("opacity", 1);
                        tooltip.transition()
                            .duration(500)
                            .style("opacity", 0);
                    }});

                // Legend
                const legend = svg.append("g")
                    .attr("font-family", "sans-serif")
                    .attr("font-size", 10)
                    .attr("text-anchor", "end")
                    .selectAll("g")
                    .data(color.domain().slice().reverse())
                    .enter().append("g")
                    .attr("transform", (d, i) => `translate(0,${{i * 20}})`);

                legend.append("rect")
                    .attr("x", width + 130)
                    .attr("width", 19)
                    .attr("height", 19)
                    .attr("fill", color);

                legend.append("text")
                    .attr("x", width + 125)
                    .attr("y", 9.5)
                    .attr("dy", "0.32em")
                    .text(d => d);

                // Tooltip
                const tooltip = d3.select("body").append("div")
                    .attr("class", "tooltip")
                    .style("opacity", 0);

                // Filter functionality
                d3.select("#filter")
                    .append("label")
                    .text(filterColumn + ": ")
                    .append("select")
                    .on("change", updateChart)
                    .selectAll("option")
                    .data(["All", ...categories])
                    .enter()
                    .append("option")
                    .text(d => d);

                function updateChart() {{
                    const selectedCategory = d3.select("#filter select").property("value");
                    
                    svg.selectAll(".bar")
                        .style("display", d => selectedCategory === "All" || d.category === selectedCategory ? null : "none");
                }}
            }})();
            """
            
            return jsonify({'d3_code': d3_code})
        
        return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        app.logger.error(f"Error processing file: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)