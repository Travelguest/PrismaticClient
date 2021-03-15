<template>
  <div id='matrix' style='height: 100%'>
  </div>
</template>

<script>
import _ from 'lodash';
import * as d3 from 'd3';

export default {
  name: 'CorrelationMatrixView',
  components: {},
  props: {
    correlationMatrix: Object
  },
  computed: {
    matrixColumn() {
      return !_.isEmpty(this.correlationMatrix)? this.correlationMatrix.columns: []
    },
    matrixCombined() {
      let combined = []
      if (!_.isEmpty(this.correlationMatrix)) {
        let length = this.matrixColumn.length;
        combined = _.flatten(JSON.parse(this.correlationMatrix.combined))
            .map((d, i)=>{
              return {
                row: this.matrixColumn[Math.floor(i/length)],
                col: this.matrixColumn[i%length],
                val: d
              }
            })
      }
      return combined;
    },
  },
  data () {
    return {
      svg: null,
      width: 0,
      height: 0,
      margin: {top: 40, right: 52, bottom: 50, left: 172},
      padding: 0.05,
    }
  },
  mounted() {
    this.initMatrix();
    this.renderMatrix();
  },
  methods: {
    initMatrix() {
      // Initialize svg
      this.width = this.$el.clientWidth;
      this.height = this.$el.clientHeight;

      this.svg = d3.select(this.$el).append('svg').attr('viewBox', [0, 0, this.width, this.height]);
    },
    renderMatrix() {
      // Remove all groups in svg
      this.svg.selectAll('g').remove();

      let heatmapContainer = this.svg
          .append('g')
          .attr('transform', `translate(${this.margin.left},${this.margin.top})`)

      // Configuration
      let xAxis = g => g
          .call(d3.axisTop(x).tickSizeOuter(0));
      let yAxis = g => g
          .call(d3.axisLeft(y).tickSizeOuter(0));
      // .call(g => g.select('.domain').remove());
      let colorScale = d3.scaleSequential()
          .domain([-1,1])
          .interpolator(d3.interpolateBrBG);
      let x = d3.scaleBand()
          .domain(this.matrixColumn)
          .padding(this.padding)
          .range([0, this.width - this.margin.right - this.margin.left]);
      let y = d3.scaleBand()
          .domain(this.matrixColumn)
          .padding(this.padding)
          .range([0, this.height - this.margin.bottom - this.margin.top]);

      // Heatmap
      heatmapContainer.append('g').call(xAxis);
      heatmapContainer.append('g').call(yAxis);
      heatmapContainer
          .selectAll('.cell')
          .data(this.matrixCombined)
          .enter()
          .append('rect')
          .attr('class', 'cell')
          .attr('x', function(d) { return x(d.col) })
          .attr('y', function(d) { return y(d.row) })
          .attr('width', x.bandwidth() )
          .attr('height', y.bandwidth() )
          .style('fill', function(d) { return colorScale(d.val)} )
          .style('opacity', 1e-6)
          .transition()
          .style('opacity', 1);

      // Heatmap interaction
      d3.selectAll('.cell')
          .on('mouseover', function(_, d){
            d3.select(this).classed('selected', true);

            d3.select('.tip')
                .style('display', 'block')
                .html(d.col + ', ' + d.row + ': ' + d.val.toFixed(2));

            d3.selectAll('.cell')
                .filter(k => !(k.col === d.col || k.row === d.row))
                .style('opacity', 0.3);
            d3.selectAll('.cell')
                .filter(k => k.col === d.col || k.row === d.row)
                .style("stroke", "black").style("stroke-width", 1);
          })
          .on('mouseout', function(){
            d3.selectAll('.cell').style('opacity', 1).style("stroke-width", 0);
          });


      // legend scale
      let legendWidth = this.margin.left/8,
          legendHeight = this.height - this.margin.top - this.margin.bottom,
          legend = this.svg.append('g')
              .attr('width', legendWidth)
              .attr('height', legendHeight)
              .attr('transform', `translate(${legendWidth*4},${this.margin.top})`);

      let stops = d3.range(-1, 1.01, 0.2).map(d => {return {offset: (d+1)/2, color: colorScale(-d), value: -d}});
      legend.append('linearGradient')
          .attr('id', 'linear-gradient')
          .attr('x2', '0%')
          .attr('y2', '100%')
          .selectAll('stop')
          .data(stops)
          .enter().append('stop')
          .attr('offset', function(d){ return (100 * d.offset) + '%'; })
          .attr('stop-color', function(d){ return d.color; });
      legend.append('rect')
          .attr('width', legendWidth)
          .attr('height', legendHeight)
          .style('fill', 'url(#linear-gradient)');
      legend.selectAll('text')
          .data(stops)
          .enter().append('text')
          .attr('dx', -5)
          .attr('y', function(d){ return legendHeight * d.offset; })
          .style('text-anchor', 'end')
          .text(function(d){ return d.value.toFixed(1)})
    }
  }
}
</script>


<style scoped>
.cell.selected {
  stroke: #000;
  stroke-width: 1px;
  opacity: 0.3;
  transform: scale(1.1, 1.1);
}

.axis .domain {
  display: none;
}
.axis .tick text.selected {
  font-weight: bold;
  font-size: 1.2em;
  fill: #47ff63;
}
.axis .tick line.selected {
  stroke: #47ff63;
}
</style>