<template>
  <div id="matrix" style="height: 100%; width: 100%"></div>
</template>

<script>
import _ from "lodash";
import * as d3 from "d3";

export default {
  name: "CorrelationMatrixView",
  components: {},
  props: {
    correlationMatrix: Object,
  },
  emits: ["selectedStockFromMatrixDiagonal", "selectedStockFromMatrix"],
  computed: {
    matrixColumn() {
      return !_.isEmpty(this.correlationMatrix)
        ? this.correlationMatrix.columns
        : [];
    },
    matrixCorr() {
      return !_.isEmpty(this.correlationMatrix)
        ? this.correlationMatrix.corr
        : [];
    },
  },
  data() {
    return {
      svg: null,
      width: 759,
      height: 598,
      margin: { top: 108, right: 150, bottom: 80, left: 199 },
      padding: 0.1,
      legend: { yaxis: 40, xaxis: 20 },
      lineData: [
        { row: "000955", col: "600200", val: 0.52342, type: "price" },
        { row: "600200", col: "000538", val: -0.05813, type: "price" },
        { row: "000078", col: "000652", val: 0.66309, type: "price" },
        { row: "603301", col: "600763", val: -0.12519, type: "price" },
        { row: "000652", col: "603288", val: -0.10912, type: "price" },
        { row: "000538", col: "600269", val: 0.60816, type: "price" },
        { row: "600436", col: "600200", val: -0.00632, type: "vol" },
        { row: "000623", col: "000078", val: 0.07383, type: "vol" },
        { row: "600763", col: "000078", val: -0.15669, type: "vol" },
        { row: "603288", col: "000652", val: -0.13302, type: "vol" },
        { row: "600269", col: "000078", val: -0.06548, type: "vol" },
      ],

      colorScheme: d3.interpolateBrBG,
      // colorScheme: d3.interpolateYlGnBu,
      // colorScheme: d3.interpolateYlGn,
      // colorScheme: d3.interpolateYlOrRd,
    };
  },
  watch: {
    correlationMatrix: function () {
      this.renderMatrix();
    },
  },
  mounted() {
    this.initMatrix();
    this.renderMatrix();
  },
  methods: {
    initMatrix() {
      // Initialize svg
      // this.width = this.$el.clientWidth;
      // this.height = this.$el.clientHeight;

      // if (this.margin.left === 0) {
      //   this.margin.left =
      //     this.width - (this.height - this.margin.top - this.margin.bottom);
      // }
      this.svg = d3
        .select(this.$el)
        .append("svg")
        .attr("viewBox", [0, 0, this.width, this.height])
        .append("g")
        .attr("transform", `translate(${this.margin.left},${this.margin.top})`);
    },
    renderMatrix() {
      // Remove all groups in svg
      this.svg.selectAll("g").remove();

      let heatmapContainer = this.svg.append("g");

      let colorScale = d3
        .scaleSequential()
        .domain([-1, 1])
        .interpolator(this.colorScheme);
      let x = d3
        .scaleBand()
        .domain(this.matrixColumn)
        .padding(this.padding)
        .range([0, this.width - this.margin.right - this.margin.left]);
      let y = d3
        .scaleBand()
        .domain(this.matrixColumn)
        .padding(this.padding)
        .range([0, this.height - this.margin.bottom - this.margin.top]);
      //let r = (x(this.matrixColumn[1]) - x(this.matrixColumn[0])) / 2;

      // Heatmap
      this.svg
        .append("g")
        .attr("class", "xAxis")
        .call(d3.axisBottom(x).tickSizeOuter(0))
        .attr(
          "transform",
          `translate(0,${this.height - this.margin.bottom - this.margin.top})`
        );
      this.svg.selectAll(".xAxis .tick text").attr("transform", "rotate(12)");

      this.svg
        .append("g")
        .attr("class", "yAxis")
        .call(d3.axisRight(y).tickSizeOuter(0))
        .attr(
          "transform",
          `translate(${this.width - this.margin.right - this.margin.left},0)`
        );

      var cell = heatmapContainer
        .selectAll(".cell")
        .data(this.matrixCorr)
        .enter();

      var cellRect = cell
        .append("rect")
        .attr("class", "cell")
        .attr("x", function (d) {
          return x(d.col);
        })
        .attr("y", (d) => y(d.row))
        .attr("width", x.bandwidth())
        .attr("height", y.bandwidth())
        .style("fill", (d) => colorScale(d.val))
        .style("opacity", 1e-6)
        .transition()
        .style("opacity", 1);

      // var cellCircle = cell
      cell
        .filter((k) => k.col == k.row)
        .append("circle")
        .attr("class", "cell")
        .attr("cx", function (d) {
          return x(d.col) + x.bandwidth() / 2;
        })
        .attr("cy", (d) => y(d.row) + y.bandwidth() / 2)
        .attr("r", x.bandwidth() / 3.25)
        .style("fill", function (d) {
          if (d.val >= 0) return colorScale(0.75);
          else return colorScale(-0.75);
        })
        .style("opacity", 0.3)
        .transition()
        .style("opacity", 0.3);

      //pieChart
      let radius = x.bandwidth() / 2.75;
      let pie = d3.pie().value((d) => d);
      let arc = d3.arc().innerRadius(x.bandwidth() / 3.25).outerRadius(radius);

      let points = heatmapContainer
        .selectAll("g")
        .data(this.matrixCorr.filter((k) => k.col === k.row))
        .enter()
        .append("g")
        .attr(
          "transform",
          (d) =>
            `translate(${x(d.col) + x.bandwidth() / 2},${
              y(d.row) + y.bandwidth() / 2
            })`
        )
        .attr("class", "pies");

      let pies = points
        .selectAll(".pies")
        .data((d) => {
          let res = pie([Math.abs(d.val), 1 - Math.abs(d.val)]); //pie()只能接受正值数组，用于pieChart的分段画弧
          res.forEach((dd) => {
            dd.dataValue = [d.val, 1];
          });
          console.log(res);
          return res;
        })
        .enter()
        .append("g")
        .attr("class", "arc")
        //.attr("class", "cell")
        .on("click", (_, d) => {
          //把事件加到整体group上
          this.$emit("selectedStockFromMatrixDiagonal", d.row);
        });

      pies
      //.attr("class", "cell")
        .append("path")
        .attr("d", arc)
        .attr("fill", (d, i) => {
          console.log("d.dataValuel:", d.dataValue); //不知道d是啥，可以console出来看看
          if (i == 0) {
            if (d.dataValue[i] < 0) {
              return colorScale(-0.75);
            } else {
              return colorScale(0.75);
            }
            //return colorScale(d.dataValue[i]);
          } else return "white";
        })
        .style("stroke", function (d, i) {
          if (i == 0) {
            if (d.dataValue[i] < 0) {
              return colorScale(-0.75);
            } else {
              return colorScale(0.75);
            }
            //return colorScale(d.dataValue[i]);
          } else return "white";
        })
        .style("stroke-width", 3);
      

      let mouseover = function (_, d) {
        d3.selectAll(".cell")
          .filter((k) => !(k.col === d.col || k.row === d.row)) // when not in the same row or column
          .style("opacity", 0.3)
          .style("stroke-width", 0);
        d3.selectAll(".cell")
          .filter(
            (k) => (k.col === d.col || k.row === d.row) && k.col !== k.row
          ) // when in the same row or column
          .style("stroke-width", 1)
          .style("stroke", (d) => {
            if (d.type === "vol") {
              //交易量下三角
              return "black";
            } else if (d.type === "price") {
              //股价上三角
              return "black";
            } else return "none";
          })
          .style("stroke-dasharray", (d) => {
            if (d.type === "vol") {
              return "2 2";
            } else return "0";
          });
          d3.selectAll(".cell")
          .filter(
            (k) => (k.col === d.col || k.row === d.row) && k.col == k.row
          ) // when in the same row or column
          .style("opacity", 0.3)
          .style("stroke-width", 0);
      };

      let mouseout = function () {
        d3.selectAll(".cell")
          .style("opacity", 1)
          .style("stroke-width", (d) => {
            if (d.col === d.row) return 4;
            else return 0;
          });
        d3.selectAll(".cell")
          .filter(
            (k) => k.col == k.row
          ) // when in the same row or column
          .style("opacity", 0.3)
          .style("stroke-width", 0);
      };

      // Heatmap interaction
      d3.selectAll(".cell").on("mouseover", mouseover).on("mouseout", mouseout);

      // The diagonal cells

      cellRect.filter((k) => k.col === k.row).style("fill", "white");

      d3.selectAll(".cell")
        //.filter((k) => k.col !== k.row)
        .on("click", (_, d) => {
          this.$emit("selectedStockFromMatrix", d.row, d.col);
        });

      //barChart
      let yScale = d3
        .scaleLinear()
        .domain(d3.extent(this.lineData, (d) => d.val))
        .range([this.margin.top / 3, 0])
        .nice();
      this.svg
        .selectAll(".barChart")
        .data(this.lineData)
        .enter()
        .append("rect")
        .attr("x", (d) => x(d.col))
        .attr("y", (d) => yScale(Math.max(0, d.val)))
        .attr("height", (d) => Math.abs(yScale(d.val) - yScale(0)))
        .attr("width", x.bandwidth())
        .style("fill", (d) => {
          if (d.val < 0) return "#C65A21";
          else return "#407FB4";
        })
        .attr("transform", "translate(0,-110)");

      let xScale = d3
        .scaleLinear()
        .domain(d3.extent(this.lineData, (d) => d.val))
        .range([0, this.margin.left / 3])
        .nice();

      this.svg
        .selectAll(".barChart")
        .data(this.lineData)
        .enter()
        .append("rect")
        .attr("x", (d) => xScale(Math.min(0, d.val)))
        .attr("y", (d) => y(d.row))
        .attr("width", (d) => Math.abs(xScale(d.val) - xScale(0)))
        .attr("height", y.bandwidth())
        .style("fill", (d) => {
          if (d.val < 0) return "#C65A21";
          else return "#407FB4";
        })
        .attr("transform", "translate(-110,0)");

      // legend scale
      let legendWidth = 138;
      let legendHeight = 15;
      let legend = this.svg.append("g").attr("transform", "translate(410,-30)");

      let stops = d3.range(-1, 1.01, 0.2).map((d) => {
        return { offset: (d + 1) / 2, color: colorScale(d), value: d };
      });
      legend
        .append("linearGradient")
        .attr("id", "linear-gradient")
        .attr("x2", "100%")
        .attr("y2", "0%")
        .selectAll("stop")
        .data(stops)
        .enter()
        .append("stop")
        .attr("offset", (d) => 100 * d.offset + "%")
        .attr("stop-color", (d) => d.color);
      legend
        .append("rect")
        .attr("width", legendWidth)
        .attr("height", legendHeight)
        .style("fill", "url(#linear-gradient)");

      legend
        .selectAll("text")
        .data([-1.0, 1.0])
        .enter()
        .append("text")
        .attr("dy", -5)
        .attr("x", (_, i) => i * 138)
        .style("text-anchor", "middle")
        .text((d) => d.toFixed(1));
    },
  },
};
</script>


<style scoped>
</style>