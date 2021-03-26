<template>
  <div class="container">
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
    stockA: String,
    stockB: String,
    preprocessedData: Object,
  },
  components: {},
  data() {
    return {
      svg: null,
      margin: { top: 10, right: 40, bottom: 30, left: 35 },
      width: 1055,
      height: 259,
      date: null,
      stockDataA: null,
      stockDataB: null,

      //   date: Object.keys(market_nav_date),
      //   marketNav: Object.values(market_nav_date),
      //   marketShares: Object.values(market_number_date),
      keys: ["Fund Market Total Asset", "Fund Market NAV"],
    };
  },
  watch: {
    preprocessedData: function () {
      console.log("title,a,b:", this.title, this.stockA, this.stockB);
      console.log("Data:", this.preprocessedData);
      if (this.title === "Stock") {
        this.dataInit();
        console.log("预处理后的", this.stockDataA, this.stockDataB);
        this.renderUpdate();
      }
    },
  },
  mounted: function () {
    this.dataInit();
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
      return d3.scaleLinear().range([this.innerHeight, 0]).nice();
    },
    linePath() {
      return d3
        .line()
        .curve(d3.curveCatmullRom)
        .x((d, i) => this.xScale(this.date[i]))
        .y((d) => this.yScale(d.close));
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
    dataInit() {
      this.date = this.preprocessedData.date.map((d) => new Date(d));
      if (this.title === "Stock") {
        this.stockDataA = this.preprocessedData[this.stockA];
        this.stockDataB = this.preprocessedData[this.stockB];
      }
    },
    renderInit() {
      //date数据处理

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
      console.log("renderUpdate了！", this.svg);
      // this.svg.selectAll("g").remove();
      // Add X axis
      this.svg
        .append("g")
        .attr("class", "xAxis")
        .call(
          d3.axisBottom(this.xScale)
          // .ticks(d3.timeYear.every(1), "%Y")
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
      // this.svg
      //   .append("g")
      //   .attr("class", "yAxis")
      //   .call(
      //     d3.axisLeft(this.yScale).tickFormat(d3.format(".0%")).ticks(5)
      //     // .ticks(d3.timeYear.every(2))
      //     // .tickValues([2010,2020])
      //     // .tickSize(this.innerHeight / 2 - 3)
      //   )
      // .select(".domain")
      // .remove();

      // this.svg
      //   .select(".yAxis")
      //   .selectAll(".tick text")
      //   .style("font-family", "Helvetica")
      //   .style("font-size", "10px")
      //   .style("color", "#6C7B8A");

      let curveChart = this.svg.append("g");

      //market shares
      //画y轴
      this.yScale.domain(d3.extent(this.stockDataA, (d) => d.close));
      this.svg
        .append("g")
        .attr("id", "yAxis_Stock_A")
        .call(
          d3.axisLeft(this.yScale)
          // .tickFormat(d3.format("~s"))
          // .ticks(5)
          // .tickFormat(d3.format(".0%")).ticks(5)
          // .ticks(d3.timeYear.every(2))
          // .tickValues([2010,2020])
          // .tickSize(this.innerHeight / 2 - 3)
        )
        .select(".domain")
        .remove();
      this.svg
        .select("#yAxis_Stock_A")
        .selectAll(".tick text")
        .style("font-family", "Helvetica")
        .style("font-size", "10px")
        .style("color", "#6C7B8A");

      curveChart
        .append("g")
        .append("path")
        .attr("class", "line_path_stock_A")
        .attr("d", this.linePath(this.stockDataA))
        .attr("fill", "none")
        .attr("stroke-width", 1.5)
        // .attr("stroke", "rgba(80,161,255,0.30)");
        .attr("stroke", "red");

      //面积图
      // curveChart
      //   .append("g")
      //   .append("path")
      //   .datum(this.marketShares)
      //   .attr("class", "streamGraphLayers")
      //   .style("stroke", "rgba(80,161,255,0.30)")
      //   .style("fill", "rgba(80,161,255,0.30)")
      //   .attr("d", this.area);

      //marketNav
      this.yScale.domain(d3.extent(this.stockDataB, (d) => d.close));
      this.svg
        .append("g")
        .attr("id", "yAxis_Stock_B")
        .call(
          d3.axisRight(this.yScale)
          // .ticks(6)
        )
        .attr("transform", `translate(${this.innerWidth},0)`)
        .select(".domain")
        .remove();
      this.svg
        .select("#yAxis_Stock_B")
        .selectAll(".tick text")
        .style("font-family", "Helvetica")
        .style("font-size", "10px")
        .style("color", "#6C7B8A");

      curveChart
        .append("g")
        .append("path")
        .attr("class", "line_path_stock_B")
        .attr("d", this.linePath(this.stockDataB))
        .attr("fill", "none")
        .attr("stroke-width", 2)
        .attr("stroke", "#FE6AAC");

      //legend
      // this.svg
      //   .selectAll(".legend")
      //   .data(this.keys)
      //   .enter()
      //   .append("circle")
      //   .attr("cx", (d, i) => 15 + i * 230)
      //   .attr("cy", -49)
      //   .attr("r", "6px")
      //   .style("fill", (d) => this.colorScale(d));

      // this.svg
      //   .selectAll(".labels")
      //   .data(this.keys)
      //   .enter()
      //   .append("text")
      //   .attr("x", (d, i) => 30 + i * 230)
      //   .attr("y", -48)
      //   .style("fill", "#9F9F9F")
      //   .style("font-family", "PingFangSC-Medium")
      //   .style("font-size", "14px")
      //   .style("letter-spacing", "-0.18px")
      //   .text((d) => d)
      //   .attr("text-anchor", "left")
      //   .style("alignment-baseline", "middle");

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
  border: 1px solid red;
}
/* #line_chart {
  height: 253px;
  width: 100%;
} */
.funds_market_style {
  margin-top: 3%;
  margin-bottom: 1%;
}
.funds_market_style text {
  font-family: "PingFangSC-Semibold";
  font-size: 19px;
  height: 32px;
  font-weight: 800;
  color: #185bbd;
  letter-spacing: 0;
  margin-left: 25px;
}
.funds_market_style .menu_icon {
  position: relative;
  color: #185bbd;
  font-size: 23px;
  bottom: 4px;
  left: 20px;
}
</style>