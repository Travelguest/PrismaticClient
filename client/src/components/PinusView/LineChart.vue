<template>
  <div class="container">
    <div>
      <a-menu
        mode="horizontal"
        @click="handleSwitchClick"
        style="width: 300px; position: absolute"
        v-model:selectedKeys="nowTag"
      >
        <a-menu-item key="close">close</a-menu-item>
        <a-menu-item key="pct">pct</a-menu-item>
        <a-menu-item key="log">log</a-menu-item>
      </a-menu>
    </div>
    <div :id="`line_chart_${id}`"></div>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: "LineChart",
  props: {
    id: String,
    title: String,
    stockA: String, //stockA的ID
    stockB: String,
    preprocessedData: Object,
  },
  components: {},
  data() {
    return {
      svg: null,
      margin: { top: 52, right: 40, bottom: 20, left: 35 },
      width: 1055,
      height: 259,
      date: null,
      dataA: null,
      dataB: null,
      keys: [],
      nowTag: ["close"],
    };
  },
  watch: {
    preprocessedData: function () {
      //第x(x>1)次刷触发的事件
      // console.log("时间轴变化~");
      this.renderUpdate();
    },
  },
  mounted: function () {
    console.log(this.title, this.preprocessedData);
    this.renderInit();
    this.renderUpdate();
  },
  emits: ["updateBrush"],
  computed: {
    innerWidth() {
      return this.width - this.margin.left - this.margin.right;
    },
    innerHeight() {
      return this.height - this.margin.top - this.margin.bottom;
    },
    xScale() {
      return d3
        .scaleTime()
        .domain([this.date[0], this.date[this.date.length - 1]])
        .range([0, this.innerWidth])
        .nice();
    },
    yScale() {
      return d3
        .scaleLinear()
        .range([this.innerHeight - 28, 28])
        .nice();
    },
    linePath() {
      let path = d3
        .line()
        .curve(d3.curveCatmullRom)
        .x((d, i) => this.xScale(this.date[i]));
      if (this.nowTag[0] === "close") {
        return path.y((d) => this.yScale(d.close));
      } else if (this.nowTag[0] === "pct") {
        return path.y((d) => this.yScale(d.pct));
      } else {
        return path.y((d) => this.yScale(d.log));
      }
    },
    colorScale() {
      return d3
        .scaleOrdinal()
        .domain(this.keys)
        .range(["rgba(80,161,255,0.30)", "#FE6AAC"]);
    },
    area() {
      return d3
        .area()
        .x((d, i) => this.xScale(this.date[i]))
        .y0(() => this.yScale(0))
        .y1((d) => this.yScale(d));
    },
  },
  methods: {
    handleSwitchClick(event) {
      //切换事件
      // console.log(this.nowTag);
      this.nowTag[0] = event.key;
      this.renderUpdate();
    },
    renderInit() {
      this.svg = d3
        .select(`#line_chart_${this.id}`)
        .append("svg")
        .attr("width", this.width)
        .attr("height", this.height)
        .attr("viewBox", [0, 0, this.width, this.height])
        .append("g")
        .attr("transform", `translate(${this.margin.left},${this.margin.top})`);
    },

    renderUpdate() {
      //date数据处理
      this.date = this.preprocessedData.date.map((d) => new Date(d));
      if (this.title === "Stock") {
        this.keys = [this.stockA, this.stockB];
        this.dataA = this.preprocessedData[this.stockA];
        this.dataB = this.preprocessedData[this.stockB];
      } else {
        this.keys = [
          this.preprocessedData.index_name,
          this.preprocessedData.stock_name,
        ];
        this.dataA = this.preprocessedData.index; //其余的dataA存储index
        this.dataB = this.preprocessedData.stock; //其余的dataB存储stock
      }
      this.svg.selectAll("g").remove();
      // Add X axis
      this.svg
        .append("g")
        .attr("class", "xAxis")
        .call(
          d3.axisBottom(this.xScale)
          // .ticks(10)
        )
        .attr("transform", `translate(0,${this.innerHeight})`);
      // .select(".domain")
      // .remove();
      this.svg
        .select(".xAxis")
        .selectAll(".tick text")
        .style("font-size", "13px")
        .style("font-family", "PingFangSC-Regular")
        .style("letter-spacing", "-0.08px")
        .style("color", "#6C7B8A");

      //画y轴——左边dataA的

      if (this.nowTag[0] === "close") {
        this.yScale.domain(d3.extent(this.dataA, (d) => d.close));
      } else if (this.nowTag[0] === "pct") {
        this.yScale.domain(d3.extent(this.dataA, (d) => d.pct));
      } else {
        this.yScale.domain(d3.extent(this.dataA, (d) => d.log));
      }

      this.svg.append("g").attr("id", "yAxis_A").call(
        d3.axisLeft(this.yScale)
        // .tickFormat(d3.format("~s"))
        //.ticks(6)
        // .tickFormat(d3.format(".0%")).ticks(5)
        // .ticks(d3.timeYear.every(2))
        // .tickValues([2010,2020])
        // .tickSize(this.innerHeight / 2 - 3)
      );
      // .select(".domain")
      // .remove();
      this.svg
        .select("#yAxis_A")
        .selectAll(".tick text")
        .style("font-family", "Helvetica")
        .style("font-size", "10px")
        .style("color", "#6C7B8A");

      let curveChart = this.svg.append("g");
      curveChart
        .append("g")
        .append("path")
        .attr("class", "line_path_A")
        .attr("d", this.linePath(this.dataA))
        .attr("fill", "none")
        .attr("stroke-width", 1.5)
        .attr("stroke", "rgba(80,161,255,0.30)");
      // .attr("stroke", "red");

      //面积图
      // curveChart
      //   .append("g")
      //   .append("path")
      //   .datum(this.marketShares)
      //   .attr("class", "streamGraphLayers")
      //   .style("stroke", "rgba(80,161,255,0.30)")
      //   .style("fill", "rgba(80,161,255,0.30)")
      //   .attr("d", this.area);

      //右侧的Y轴
      if (this.nowTag[0] === "close") {
        this.yScale.domain(d3.extent(this.dataB, (d) => d.close));
      } else if (this.nowTag[0] === "pct") {
        this.yScale.domain(d3.extent(this.dataB, (d) => d.pct));
      } else {
        this.yScale.domain(d3.extent(this.dataB, (d) => d.log));
      }
      this.svg
        .append("g")
        .attr("id", "yAxis_B")
        .call(
          d3.axisRight(this.yScale)
          //  .ticks(6)
        )
        .attr("transform", `translate(${this.innerWidth},0)`);
      // .select(".domain")
      // .remove();
      this.svg
        .select("#yAxis_B")
        .selectAll(".tick text")
        .style("font-family", "Helvetica")
        .style("font-size", "10px")
        .style("color", "#6C7B8A");

      curveChart
        .append("g")
        .append("path")
        .attr("class", "line_path_B")
        .attr("d", this.linePath(this.dataB))
        .attr("fill", "none")
        .attr("stroke-width", 2)
        .attr("stroke", "#FE6AAC");

      // legend
      this.svg
        .selectAll(".legend")
        .data(this.keys)
        .enter()
        .append("circle")
        .attr("cx", (d, i) => 350 + i * 180)
        .attr("cy", -26)
        .attr("r", "6px")
        .style("fill", (d) => this.colorScale(d));

      this.svg
        .selectAll(".labels")
        .data(this.keys)
        .enter()
        .append("text")
        .attr("x", (d, i) => 365 + i * 180)
        .attr("y", -24)
        .style("fill", "#9F9F9F")
        .style("font-family", "PingFangSC-Medium")
        .style("font-size", "14px")
        .style("letter-spacing", "-0.18px")
        .text((d) => d)
        .attr("text-anchor", "left")
        .style("alignment-baseline", "middle");

      //删除刻度线
      // this.svg.selectAll(".tick line").remove();

      //timebrush
      // let brush = d3
      //   .brushX()
      //   .extent([
      //     [0, -this.margin.top + 65],
      //     [this.innerWidth, this.innerHeight],
      //   ])
      //   .on("end", this.updateDate);
      // this.svg.append("g").attr("class", "brush").call(brush);
    },
  },
};
</script>

<style scoped>
.container {
  height: 260px;
  width: 100%;
  /* border: 1px solid red; */
}
/* #line_chart {
  height: 253px;
  width: 100%;
} */
</style>