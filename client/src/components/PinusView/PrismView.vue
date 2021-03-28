<template>
  <div>
    <!-- <div id="knowledge_graph_title"><div id="knowledge_graph_text">Knowledge Graph</div></div>
    <div id="triangle"></div> -->
    <div id="prism_view_container">
      <div :id="`pinus_${id}`" style="height: 100%; width: 100%"></div>
      <div :id="`pinus_${id}_svg`"></div>
      <div :id="`tooltip_${id}`" class="tooltip"></div>
    </div>
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
    correlationTriangle: Object,
    title: String,
  },
  data() {
    return {
      canvas: null,
      custom: null,
      cellSize: null,
      width: 220,
      height: 220,
      totalHeight: 0,
      margin: { top: 0, right: 0, bottom: 0, left: 10 },
      padding: 0.0,
      svg: null,
      date: null,

      // colorScheme: d3.interpolateBrBG,
      // colorScheme: d3.interpolateYlGnBu,
      colorScheme: d3.interpolateRdYlGn,
      // colorScheme: d3.interpolateYlGn,
      // colorScheme: d3.interpolateYlOrRd,
    };
  },
  watch: {
    correlationTriangle: function () {
      // console.log("correlationTriangle改变了:",this.id, this.correlationTriangle);
      console.log("ID:", this.id);
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
        .range([this.margin.left, this.margin.left + this.width])
        .nice();
    },
    yScale() {
      return d3
        .scaleLinear()
        .domain([this.matrixRow[0], this.matrixRow[this.matrixRow.length - 1]])
        .range([this.margin.top, this.margin.top + this.height - 7])
        .nice();
    },
  },
  mounted() {
    this.initPinus();
  },
  emits: ["updateBrush"],
  methods: {
    updateDate({ selection }) {
      if (selection && this.correlationTriangle) {
        let start = this.xScale.invert(selection[0]).toISOString().slice(0, 10);
        let end = this.xScale.invert(selection[1]).toISOString().slice(0, 10);
        if (start !== end) {
          // const queryCodes = this.correlationTriangle.name.split(" against ");
          this.$emit("updateBrush", start, end, this.title);
        }
      }
    },
    initPinus() {
      // Initialize canvas
      // this.width = this.$el.clientWidth;
      this.totalHeight = this.$el.clientHeight;
      // this.width = 220;
      // this.height = 220;
      // console.log("width height:",this.width,this.height);

      this.canvas = d3
        .select(`#pinus_${this.id}`)
        .append("canvas")
        .attr("width", this.width)
        .attr("height", this.height);

      this.custom = d3.select(document.createElement("custom"));
      this.svg = d3
        .select(`#pinus_${this.id}_svg`)
        .append("svg")
        .attr("width", this.width + 30)
        .attr("height", this.height + 30)
        // .attr("fill", "red")
        // .attr("transform", `translate(0,${-this.height})`)
        .style("position", "absolute")
        .style("top", 6)
        .style("left", 45)
        .append("g")
        .style("z-index", "1");

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

      let join = this.custom.selectAll("custom.rect").data(this.matrixCorr);
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
      this.date = this.matrixColumn.map((d) => new Date(d));
      this.svg.selectAll("g").remove();

      //var backGroundColorSize=[[0,this.height],[50,this.height],[50,this.height/3],[0,this.height/3]];

      this.svg
        .append("rect")
        .attr("class", "backGround")
        .attr("x", 2)
        .attr("y", 5)
        .attr("width", 8)
        .attr("height", this.height / 3)
        .style("fill", "#2D5B81");

      this.svg
        .append("g")
        .attr("class", "xAxis")
        .call(
          d3
            .axisBottom(this.xScale)
            // .ticks(d3.timeMonth.every(1))
            .tickFormat(d3.timeFormat("%b"))
        )
        .attr("transform", `translate(0,${this.height - 6})`)
        .select(".domain")
        .remove();
      this.svg
        .append("g")
        .attr("class", "yAxis")
        .call(
          d3.axisRight(this.yScale).ticks(2)
          // .tickFormat(d3.timeFormat("%b"))
        )
        .attr("transform", `translate(${this.height},0)`)
        .select(".domain")
        .remove();

      this.svg
        .append("rect")
        .attr("class", "brushBackGround")
        .attr("x", 0)
        .attr("y", 22)
        .attr("width", this.width)
        .attr("height", "15")
        .style("fill", "#E9E9E9")
        // .style("fill", "red")
        .attr("transform", `translate(0,${this.height - 6})`);

      if (!this.correlationTriangle)
        this.svg.selectAll(".brushBackGround").remove();
      if (!this.correlationTriangle) this.svg.selectAll(".backGround").remove();

      //

      let brush = d3
        .brushX()
        .extent([
          [0, 0],
          [this.innerWidth, 38],
        ])
        .on("end", this.updateDate);
      this.svg.select(".brush").remove();
      this.svg
        .append("g")
        .attr("class", "brush")
        .call(brush)
        .attr("transform", `translate(0,${this.height - 7})`);

      //Title
      this.svg
        .append("g")
        .append("text")
        .attr("x", 15)
        .attr("y", 25)
        .text(this.title)
        .style("fill", "#2D5B81")
        .style("font-size", "25px");

      //文本2
      this.svg
        .append("g")
        .append("text")
        .attr("x", 15)
        .attr("y", 45)
        .text(this.title)
        .style("fill", "#2D5B81")
        .style("font-size", "15px");

      //文本3
      this.svg
        .append("g")
        .append("text")
        .attr("x", 15)
        .attr("y", 60)
        .text(this.title)
        .style("fill", "#2D5B81")
        .style("font-size", "15px");
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

      d3.select(`#pinus_${id}_svg`).on("mousemove", function (mouse) {
        // console.log(mouse.x, mouse.y);
        // get mousePositions from the main canvas
        let mouseX = mouse.layerX;
        let mouseY = mouse.layerY;
        // console.log(mouseX, mouseY);
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
        // console.log("x,y", x, y);
        if (x && y) {
          // console.log(d3.select(`#tooltip_${id}`));
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
  z-index: 99;
}
#pinus_topDetail_svg {
  height: 220px;
  width: 220px;
}
#pinus_bottomDetail_svg {
  height: 220px;
  width: 220px;
}
#prism_view_container {
  height: 100%;
  width: 100%;
  position: absolute;
}

#knowledge_graph_title {
  position: absolute;
  right: 0;
  top: 0;
  padding: 0 20px;
  width: 50%;
  height: 40px;
  line-height: 40px;
  font-size: 26px;
  background: #777;
  color: #fcfcfc;
  display: flex;
  font-weight: bold;
  border-radius: 2px;
  box-shadow: 0 1px 2px rgba(26 26 26 0.2);
}

#knowledge_graph_text {
  position: absolute;
  right: 0;
  padding-right: 20px;
  text-align: right;
}

#triangle {
  position: absolute;
  top: 0;
  right: 49%;
  border-top: 40px solid #777;
  border-left: 45px solid #ffffff;
  border-bottom: 3px solid #ffff;
}
</style>