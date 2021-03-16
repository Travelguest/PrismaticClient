<template>
  <div style='height: 100%'>
    <a-spin :spinning="loadingTriangle" :delay="500">
      <div id='pinus' style='height: 100%'>
        <div id="tooltip"></div>
      </div>
    </a-spin>
  </div>
</template>

<script>
import _ from 'lodash';
import * as d3 from 'd3';

export default {
  name: 'PinusView',
  components: {},
  props: {
    loadingTriangle: Boolean,
    correlationTriangle: Object,
  },
  computed: {
    matrixColumn() {
      return !_.isEmpty(this.correlationTriangle)? this.correlationTriangle.date: []
    },
    matrixRow() {
      return !_.isEmpty(this.correlationTriangle)? this.correlationTriangle.window: []
    },
    matrixCorr() {
      return !_.isEmpty(this.correlationTriangle)? this.correlationTriangle.corr: []
    },
  },
  data () {
    return {
      canvas: null,
      custom: null,
      width: 0,
      height: 0,
      margin: {top: 40, right: 40, bottom: 40, left: 40},
      padding: 0.01,

      // colorScheme: d3.interpolateBrBG,
      // colorScheme: d3.interpolateYlGnBu,
      colorScheme: d3.interpolateRdYlGn,
      // colorScheme: d3.interpolateYlGn,
      // colorScheme: d3.interpolateYlOrRd,

    }
  },
  watch: {
    correlationTriangle: function() {
      this.bindPinus();

      let _this = this;
      let t = d3.timer(function(elapsed) {
        _this.renderPinus();
        if (elapsed > 2000) t.stop();
      });
    }
  },
  mounted() {
    this.initPinus();
  },
  methods: {
    initPinus() {
      // Initialize canvas
      this.width = this.$el.clientWidth;
      this.height = this.$el.clientHeight;
      this.canvas = d3.select('#pinus')
          .append('canvas')
          .classed('mainCanvas', true)
          .attr('width', this.width)
          .attr('height', this.height);

      this.custom = d3.select(document.createElement('custom'));

      this.bindPinus();

      let _this = this;
      let t = d3.timer(function(elapsed) {
        _this.renderPinus();
        if (elapsed > 2000) t.stop();
      });
    },
    bindPinus() {
      let numRow = this.matrixRow.length,
          cellSize = ((this.width-this.margin.left-this.margin.right) / numRow) - this.padding;

      let colorScale = d3.scaleSequential()
          .domain([-1,1])
          .interpolator(this.colorScheme);

      let join = this.custom.selectAll('custom.rect').data(this.correlationTriangle.corr);
      let enterSel = join.enter()
          .append('custom')
          .attr('class', 'rect')
          .attr('x', (_, i) => {
            let K = Math.floor((Math.sqrt(8*i+1)-1)/2);
            return this.margin.left + (this.padding + cellSize) * // Math.floor(i/numRow) // Trivial sqaure
                (numRow - 1 - (i - Math.floor(K*(K+1)/2)))
          })
          .attr('y', (_, i) => {
            let K = Math.floor((Math.sqrt(8*i+1)-1)/2);
            return this.margin.top + (this.padding + cellSize) * K // (i%numRow) Trivial square
          })
          .attr('width', 0)
          .attr('height', 0)

      join.merge(enterSel)
          .transition()
          .attr('width', cellSize)
          .attr('height', cellSize)
          .attr('x', (_, i) => {
            let K = Math.floor((Math.sqrt(8*i+1)-1)/2);
            return this.margin.left + (this.padding + cellSize) * // Math.floor(i/numRow) // Trivial sqaure
                (numRow - 1 - (i - Math.floor(K*(K+1)/2)))
          })
          .attr('y', (_, i) => {
            let K = Math.floor((Math.sqrt(8*i+1)-1)/2);
            return this.margin.top + (this.padding + cellSize) * K // (i%numRow) Trivial square
          })
          .attr('fillStyle', (d) => (d === 2)? '#E6E6E6': colorScale(d) );

      join.exit()
          .transition()
          .attr('width', 0)
          .attr('height', 0)
          .remove();
    },
    renderPinus() {
      let context = this.canvas.node().getContext('2d');

      context.clearRect(0, 0, this.width, this.height);

      this.custom
          .selectAll('custom.rect')
          .each(function() {
            var node = d3.select(this);
            context.fillStyle = node.attr('fillStyle');
            context.fillRect(node.attr('x'), node.attr('y'), node.attr('width'), node.attr('height'))
          });
    },
    tooltip() {
      d3.select('.mainCanvas').on('mousemove', function() {
        // // draw the hiddenCanvas
        // draw(hiddenCanvas, true);
        //
        // // get mousePositions from the main canvas
        // var mouseX = d3.event.layerX || d3.event.offsetX;
        // var mouseY = d3.event.layerY || d3.event.offsetY;
        //
        //
        // // get the toolbox for the hidden canvas
        // var hiddenCtx = hiddenCanvas.node().getContext('2d');
        //
        // // Now to pick the colours from where our mouse is then stringify it in a way our map-object can read it
        // var col = hiddenCtx.getImageData(mouseX, mouseY, 1, 1).data;
        // var colKey = 'rgb(' + col[0] + ',' + col[1] + ',' + col[2] + ')';
        //
        // // get the data from our map !
        // var nodeData = colourToNode[colKey];
        //
        // log(nodeData);
        // if (nodeData) {
        //
        //   // Show the tooltip only when there is nodeData found by the mouse
        //
        //   d3.select('#tooltip')
        //       .style('opacity', 0.8)
        //       .style('top', d3.event.pageY + 5 + 'px')
        //       .style('left', d3.event.pageX + 5 + 'px')
        //       .html(nodeData.value);
        //
        // } else {
        //
        //   // Hide the tooltip when there our mouse doesn't find nodeData
        //
        //   d3.select('#tooltip')
        //       .style('opacity', 0);
        // }
      });
    }
  }
}
</script>


<style scoped>
div#tooltip {
  position: absolute;
  display: inline-block;
  padding: 10px;
  /*font-family: 'Open Sans' sans-serif;*/
  color: #000;
  background-color: #fff;
  border: 1px solid #999;
  border-radius: 2px;
  pointer-events: none;
  opacity: 0;
  z-index: 1;
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