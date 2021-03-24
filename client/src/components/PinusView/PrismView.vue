<template>
  <div style="height: 100%; width: 100%">
    <a-spin :spinning="loadingTriangle" :delay="100">
      <div :id="`pinus_${id}`" style="height: 100%">
        <div :id="`tooltip_${id}`" class="tooltip"></div>
      </div>
    </a-spin>
  </div>
</template>

<script>
import _ from "lodash";
import * as d3 from "d3";

export default {
  name: "PrismView",
  components: {},
  props: {
    id: String,
    loadingTriangle: Boolean,
    correlationTriangle: Object,
  },
  
  data() {
    return {
      canvas: null,
      custom: null,
      cellSize: null,
      width: 0,
      height: 0,
      totalHeight: 0,
      margin: { top: 0, right: 0, bottom: 0, left: 10 },
      padding: 0.0,
      svg: null,
      date:null,

      // colorScheme: d3.interpolateBrBG,
      // colorScheme: d3.interpolateYlGnBu,
      colorScheme: d3.interpolateRdYlGn,
      // colorScheme: d3.interpolateYlGn,
      // colorScheme: d3.interpolateYlOrRd,
    };
  },
  watch: {
    correlationTriangle: function () {
      this.bindPinus();

      this.initTooltip();
      this.renderArea();

      let _this = this;
      let t = d3.timer(function (elapsed) {
        _this.renderPinus();
        if (elapsed > 2000) t.stop();
      });
    },
  },
  computed: {
    innerWidth() {
      return this.width - this.margin.left - this.margin.right;
    },
    innerHeight() {
      return this.height - this.margin.top - this.margin.bottom;
    },
    indexName() {
      return !_.isEmpty(this.correlationTriangle)
        ? this.correlationTriangle.name
        : "";
    },
    matrixColumn() {
      return !_.isEmpty(this.correlationTriangle)
        ? this.correlationTriangle.date
        : [];
    },
    matrixRow() {
      return !_.isEmpty(this.correlationTriangle)
        ? this.correlationTriangle.window
        : [];
    },
    matrixCorr() {
      return !_.isEmpty(this.correlationTriangle)
        ? this.correlationTriangle.corr
        : [];
    },
    squareLength() {
      return this.height - this.margin.top - this.margin.bottom;
    },
    xScale() {
      return d3
        .scaleTime()
        .domain([this.date[0], this.date[this.date.length - 1]])
        .range([12, this.innerWidth-12])
        .nice();
    },
  },
  mounted() {
    console.log("correlationTriangle:", this.correlationTriangle);
    this.initPinus();
  },
  methods: {
    initPinus() {
      // Initialize canvas
      // this.width = this.$el.clientWidth;
      this.totalHeight = this.$el.clientHeight;
      this.width = 220;
      this.height = 220;
      // console.log("width height:",this.width,this.height);

      this.date = this.matrixColumn.map(d => new Date(d));


      this.canvas = d3
        .select(`#pinus_${this.id}`)
        .append("canvas")
        .attr("width", this.width)
        .attr("height", this.height);

      this.custom = d3.select(document.createElement("custom"));
      this.svg = d3
        .select(`#pinus_${this.id}`)
        .append("svg")
        .attr("width", this.width)
        .attr("height", this.totalHeight - this.height)
        .append("g");
      // .attr("transform", `translate(${this.margin.left},${this.width})`);

      this.bindPinus();
      this.initTooltip();
      this.renderArea();

      let _this = this;
      let t = d3.timer(function (elapsed) {
        _this.renderPinus();
        if (elapsed > 2000) t.stop();
      });
    },
    bindPinus() {
      let numRow = this.matrixRow.length,
        cellSize = this.squareLength / numRow - this.padding;
      this.cellSize = cellSize;
      this.margin.right = this.width - this.margin.left - this.squareLength;

      let colorScale = d3
        .scaleSequential()
        .domain([-1, 1])
        .interpolator(this.colorScheme);

      let join = this.custom
        .selectAll("custom.rect")
        .data(this.correlationTriangle.corr);
      let enterSel = join
        .enter()
        .append("custom")
        .attr("class", "rect")
        .attr("x", (_, i) => {
          let K = Math.floor((Math.sqrt(8 * i + 1) - 1) / 2);
          return (
            this.margin.left +
            (this.padding + cellSize) *
              (numRow - 1 - K + i - Math.floor((K * (K + 1)) / 2))
          );
        })
        .attr("y", (_, i) => {
          let K = Math.floor((Math.sqrt(8 * i + 1) - 1) / 2);
          return this.margin.top + (this.padding + cellSize) * K;
        })
        .attr("width", 0)
        .attr("height", 0);

      join
        .merge(enterSel)
        .transition()
        .attr("width", cellSize)
        .attr("height", cellSize)
        .attr("x", (_, i) => {
          let K = Math.floor((Math.sqrt(8 * i + 1) - 1) / 2);
          return (
            this.margin.left +
            (this.padding + cellSize) *
              (numRow - 1 - K + i - Math.floor((K * (K + 1)) / 2))
          );
        })
        .attr("y", (_, i) => {
          let K = Math.floor((Math.sqrt(8 * i + 1) - 1) / 2);
          return this.margin.top + (this.padding + cellSize) * K;
        })
        .attr("fillStyle", (d) => (d === 2 ? "#E6E6E6" : colorScale(d)));

      join.exit().transition().attr("width", 0).attr("height", 0).remove();
    },
    renderArea() {
      this.svg
        .append("g")
        .attr("class", "xAxis")
        .call(d3.axisTop(this.xScale).ticks(d3.timeMonth.every(2)))
        .attr("transform", `translate(0,18)`)
        .select(".domain")
        .remove();
    let area = this.svg
        .append("rect")
        .attr("x", 0)
        .attr("y", 18)
        .attr("width", this.width)
        .attr("height", "20")
        .style("fill", "#E9E9E9");
    
      let brush = d3
        .brushX()
        .extent([
          [0, 0],
          [this.width, 20],
        ])
        // .on("end", this.updateDate);
      area.append("g").attr("class", "brush").call(brush);
    },
    renderPinus() {
      let context = this.canvas.node().getContext("2d");

      context.clearRect(0, 0, this.width, this.height);

      this.custom.selectAll("custom.rect").each(function () {
        var node = d3.select(this);
        context.fillStyle = node.attr("fillStyle");
        context.fillRect(
          node.attr("x"),
          node.attr("y"),
          node.attr("width"),
          node.attr("height")
        );
      });
    },
    initTooltip() {
      let margin = this.margin,
        id = this.id,
        numRow = this.matrixRow.length,
        _this = this;

      d3.select(`#pinus_${id}`).on("mousemove", function (mouse) {
        // get mousePositions from the main canvas
        let mouseX = mouse.layerX;
        let mouseY = mouse.layerY;

        let x,
          y,
          corr = null;

        // linear programming to determine in-triangle position
        if (
          mouseY <= _this.height - margin.bottom &&
          mouseX <= _this.width - margin.right &&
          mouseY >= -mouseX + margin.left + margin.top + _this.squareLength
        ) {
          x = numRow - 1 - parseInt((mouseX - margin.left) / _this.cellSize);
          y = parseInt((mouseY - margin.top) / _this.cellSize);
          corr = Math.floor(((y + 1) * (y + 2)) / 2) - 1 - x;
          corr = _this.matrixCorr[corr];
          corr =
            corr === undefined || corr === 2 ? "suspended" : corr.toFixed(4);
          x = _this.matrixColumn[numRow - 1 - x];
          y = _this.matrixRow[y];
        }

        if (x && y) {
          d3.select(`#tooltip_${id}`)
            .style("opacity", 0.8)
            .style("top", mouseY + 5 + "px")
            .style("left", mouseX + 5 + "px")
            .html(`${_this.indexName}<br>${x}<br>${y} days corr: ${corr}`);
        } else {
          d3.select(`#tooltip_${id}`).style("opacity", 0);
        }
      });
    },
  },
};
</script>


<style scoped>
.tooltip {
  position: absolute;
  display: inline-block;
  padding: 10px;
  /*font-family: 'Open Sans' sans-serif;*/
  width: 200px;
  height: 85px;
  background-color: #fff;
  border: 1px solid #999;
  border-radius: 2px;
  pointer-events: none;
  opacity: 0;
  z-index: 1;
}
</style>