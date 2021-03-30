<template>
  <div></div>
</template>

<script>
import * as d3 from "d3";
import _ from "lodash";
export default {
  name: "DynamicGraphView",
  components: {},
  props: {
    corrDistribution: Object,
    corrCluster: Object,
    corrClusterUpdate: Number,
    selectedStock: Array,
    thresholdRange: Array,
  },
  emits: ["clickedYear", "updateYearBrush"],
  data() {
    return {
      svg: null,
      width: 0,
      height: 1175,

      distWidth: 80,
      distHeight: 105,
      distPaddingHeight: 12,
      distPaddingWidth: 20,

      graphMaxNodes: 30,

      color: d3.schemeTableau10,

      yearSelected: "2020",
      // correlationRange: [0.6, 1],
      correlationMarks: { 0.6: "0.6", 0: "0", 1: "1" },
      correlatedStocks: [],
    };
  },
  watch: {
    corrDistribution: function () {
      // console.log("corrDistribution改变了：", this.corrDistribution);
      // console.log("selectedStock变了:", this.selectedStock);
      this.svg.selectAll(".dist").remove();
      this.renderDistChart();
      // this.renderGraph();
    },
    corrCluster: function () {
      //直接修改无法监测到
      // console.log("corrCluster改变了", this.corrCluster);
      this.svg.selectAll(".graph").remove();
      this.renderNodeLink();
      // this.renderGraph();
    },
    corrClusterUpdate: function () {
      // console.log("corrClusterUpdate告诉我数据：", this.corrCluster);
      this.svg.selectAll(".graph").remove();
      this.renderNodeLink();
    },
    periodRange: function () {
      this.$emit("update-period-range", this.periodRange);
    },
  },
  computed: {},
  mounted: function () {
    // console.log("corrDistribution:", this.corrDistribution);
    // console.log("corrCluster:", this.corrCluster);
    // console.log("selectedStock:", this.selectedStock);
    this.initGraph();
    this.renderGraph();
  },
  methods: {
    initGraph() {
      this.width = this.$el.clientWidth;

      this.svg = d3
        .select(this.$el)
        .append("svg")
        .attr("viewBox", [0, 0, this.width, this.height]);
    },
    renderGraph() {
      // Remove all groups in svg
      this.svg.selectAll("g").remove();

      this.renderNodeLink();
      this.renderDistChart();
    },
    renderNodeLink() {
      let _this = this;
      let graphWidth = this.width - this.distWidth - this.distPaddingWidth * 3;
      let graphHeight = this.distHeight + this.distPaddingHeight;
      let resultNodes = {};

      //topNodes:根据betweenness重要性排序后又按components分组后得到的股票代码数组
      let topNodes = Object.fromEntries(
        Object.entries(this.corrCluster).map(([k, v]) => [
          k,
          Object.entries(v.betweenness)
            .sort((a, b) => b[1] - a[1]) // descending order
            // .slice(0, this.graphMaxNodes) // select top n
            .map((x) => x[0]) // keep only keys
            .sort((x, y) => v.components[x] - v.components[y]), //再按compoents升序排序
          // .filter(id => this.selectedStock.includes(id))
        ])
      );

      // console.log("数组：", Object.entries(this.corrCluster));
      // console.log("topNodes", topNodes);

      //graphY : yScale()
      let graphY = d3
        .scalePoint()
        .domain(Object.keys(this.corrCluster).sort().reverse()) //year.reverse()
        .range([
          this.distHeight * 0.75 + 3,
          this.distHeight * 0.75 + 3 + graphHeight * 9,
        ]);

      let container = this.svg
        .selectAll(".graph")
        // .data(Object.entries(this.corrCluster).sort((a, b)=>(a[0]<b[0]?1: -1)))
        .data(Object.keys(this.corrCluster).sort().reverse())
        .enter()
        .append("g")
        .attr("class", "graph")
        .attr(
          "transform",
          (d) =>
            `translate(${this.distWidth + this.distPaddingWidth * 2}, ${graphY(
              d
            )})`
        );

      container
        .append("rect")
        .attr("class", "background")
        .attr("x", -5)
        .attr("y", this.distPaddingHeight - this.distHeight * 0.75)
        .attr("width", graphWidth + 10)
        .attr("height", graphHeight - this.distPaddingHeight)
        .style("fill", "#ECEFF1")
        .on("click", (_, d) => {
          _this.$emit("clickedYear", resultNodes[d], d); //该年的结点列表，年份
        });

      //text
      container
        .append("text")
        .attr("x", graphWidth - 115)
        .attr("y", -20)
        .text((d) => d)
        .style("font-size", "48px")
        .style("fill", "white")
        // .style("stroke","#455A64")
        // .style("stroke-width", "0.5px")
        .style("font-weight", "700")
        .style("opacity", 1);

      container
        .append("text")
        .attr("x", 20)
        .attr("y", -37)
        .text((d) => "total: " + topNodes[d].length)
        .style("font-size", "18px")
        .style("fill", "#546E7A")
        .style("font-weight", "700");
      // .style("opacity", 0.3);

      // draw the node link diagram
      //year,index,group...
      container.each((d, i, c) => {
        let container = d3.select(c[i]);
        // console.log("each:", d, i, c);
        let last = 0;
        let cnt = [];
        let temp = 0;
        let showComponents = []; //选择的股票的族号
        let idRank = [];
        let index = 0;
        //计算每个族有几个结点
        topNodes[d].forEach((id) => {
          if (this.selectedStock.includes(id)) {
            showComponents.push(this.corrCluster[d].components[id]);
          }
          if (this.corrCluster[d].components[id] != last) {
            //新组
            index = 0;
            idRank.push(index++);
            last = this.corrCluster[d].components[id];
            cnt.push(temp);
            temp = 1; //发现第一个不同的
          } else {
            temp++;
            idRank.push(index++);
            // index++;
          }
        });
        cnt.push(temp); //最后一组
        // console.log("cnt:", d, cnt);
        // console.log("idRank:", d, idRank);

        showComponents = Array.from(new Set(showComponents));
        // console.log("showComponents:",showComponents);

        let xScale = Object.fromEntries(
          Object.entries(topNodes).map(([k, v]) => [
            k,
            d3
              .scaleBand()
              // .scalePoint()
              .domain(
                v
                // v.filter((id) =>
                //   showComponents.includes(this.corrCluster[d].components[id])
                // )
              ) //筛选出和选中的标签属于同一个组的
              .range([10, graphWidth - 10])
              .padding([1]),
          ])
        );
        container
          .selectAll(".nodeContainer")
          .data(cnt)
          .enter()
          .append("rect")
          .attr("class", "nodeContainer")
          .attr("x", (_, i) => {
            let start = 0;
            for (let j in cnt) {
              if (j < i) start += cnt[j]; //不包含自己的长度
            }
            return xScale[d](topNodes[d][start]);
            //  - xScale[d].bandwidth() / 3;
          })
          .attr("y", -15)
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("height", 30)
          .attr("width", (length, i) => {
            let start = 0;
            for (let j in cnt) {
              if (j < i) start += cnt[j]; //不包含自己的长度
            }
            let end = start + length - 1;
            if (start !== end) {
              if (i === _.sum(cnt) - 1)
                return (
                  xScale[d](topNodes[d][end]) - xScale[d](topNodes[d][start])
                  // xScale[d].bandwidth() / 3
                );
              else
                return (
                  xScale[d](topNodes[d][end]) - xScale[d](topNodes[d][start])
                  // xScale[d].bandwidth()
                );
            } else return 0;
          })
          .style("fill", "none")
          .style("stroke", "#607D8B")
          .style("stroke-width", 1);

        // draw the xAxis
        container
          .append("g")
          .attr("class", "xAxis")
          .call(d3.axisBottom(xScale[d]).tickSizeOuter(0))
          // .ticks(10)
          .call((g) => g.selectAll(".tick").remove());
        // console.log(`${d}year,bandwidth:`, xScale[d].bandwidth())

        let resNodes = [];
        // draw node to the axis
        container
          .selectAll(".node")
          .data(
            topNodes[d].filter((id, index) => {
              if (
                this.selectedStock.includes(id) ||
                idRank[index] < this.graphMaxNodes
              ) {
                resNodes.push(id);
                return true;
              } else return false;
            })
            // .filter((id) => this.selectedStock.includes(id))
          )
          .enter()
          .append("circle")
          .attr("class", "node")
          .attr("id", (node) => node)
          .attr("cx", (node) => xScale[d](node))
          .attr("r", "4px")
          .style("fill", "#A1887F");
        resultNodes[d] = _.cloneDeep(resNodes);
        // console.log("resultNodes: ", resultNodes);

        // draw a vertical line to link the same node in last year
        if (i !== 0) {
          let lastD = "" + (2021 - i);
          container
            .selectAll(".linkage")
            .data(
              topNodes[d].filter(
                (id) =>
                  this.selectedStock.includes(id) &&
                  topNodes[lastD].includes(id)
              )
            ) //上一年出现过该股票
            .enter()
            .append("path")
            .attr("class", "linkage")
            .attr("id", (node) => node)
            .attr("d", (node) => {
              // provide more points for curvy effect
              let path = [
                { x: xScale[lastD](node), y: -graphHeight },
                { x: xScale[lastD](node), y: -graphHeight + 30 },
                { x: xScale[d](node), y: -30 },
                { x: xScale[d](node), y: 0 },
              ];
              return d3
                .line()
                .curve(d3.curveBasis)
                .x((d) => d.x)
                .y((d) => d.y)(path);
            })
            .attr("stroke", "#A1887F")
            .attr("fill", "none");
        }
      });

      this.svg.selectAll(".node").raise();
    },
    renderDistChart() {
      let _this = this;
      let distX = d3.scaleLinear().domain([799, 0]).range([0, this.distWidth]); // x is count
      let distY = d3
        .scaleLinear()
        .domain([1, -0.5])
        .range([0, this.distHeight]); // y is correlation
      let stockLine = d3
        .line()
        .curve(d3.curveCatmullRom)
        .x((d) => distX(d)) //sci中的数量
        .y((_, i) => distY(-0.5 + i * 0.05));
      let indexArea = d3
        .area()
        .x0(distX(0))
        .x1((d) => distX(d))
        .y((_, i) => distY(-0.5 + i * 0.05));
      let removedDistTickText = false;

      // Distribution charts container
      this.svg
        .selectAll(".dist")
        // sort to have 2020 be the first year to display
        .data(
          Object.entries(this.corrDistribution).sort((a, b) =>
            a[0] < b[0] ? 1 : -1
          )
        )
        .enter()
        .append("g")
        .attr("class", "dist")
        .attr(
          "transform",
          (_, i) =>
            `translate(${0},${
              this.distPaddingHeight +
              (this.distHeight + this.distPaddingHeight) * i
            })`
        )
        .each((d, i, c) => {
          // console.log(d, i, c);
          let container = d3.select(c[i]);
          // x-axis
          container
            .append("g")
            .attr("class", "xAxis")
            .attr("transform", `translate(0, ${_this.distHeight})`)
            .call(d3.axisTop(distX).ticks(4).tickSize(_this.distHeight))
            .call((g) => g.select(".domain").remove())
            .call((g) =>
              g
                .selectAll(".tick line")
                .attr("stroke-opacity", 0.2)
                .attr("stroke-dasharray", "1,1")
            )
            .call((g) => {
              g.selectAll(".tick text")
                .attr("dx", 0)
                .attr("dy", 0)
                .style("font-family", "Helvetica")
                .style("color", "#546E7A");
              if (removedDistTickText) {
                g.selectAll(".tick text").remove();
              } else {
                removedDistTickText = true;
              }
            });
          // y-axis
          container
            .append("g")
            .attr("class", "yAxis")
            .attr("transform", `translate(${_this.distWidth},0)`)
            .call(d3.axisRight(distY).ticks(3));
          container
            .selectAll(".yAxis")
            .selectAll(".tick text")
            .style("font-family", "Helvetica")
            .style("color", "#546E7A");

          let updateDate = ({ selection }) => {
            // console.log("selection:", selection);
            if (selection) {
              let start = parseFloat(distY.invert(selection[0]).toFixed(2));
              let end = parseFloat(distY.invert(selection[1]).toFixed(2));
              // .toISOString().slice(0, 10);
              if (start !== end) {
                // console.log("start,end:", start, end, d[0]);
                this.$emit("updateYearBrush", end, start, d[0]); //left,right,year
              }
            }
          };
          // console.log("thresholdRange:", this.thresholdRange);
          let topThreshold = distY(this.thresholdRange[1]);
          let bottomThreshold = distY(this.thresholdRange[0]);

          let brush = d3
            .brushY()
            .extent([
              [_this.distWidth, topThreshold],
              [_this.distWidth + 32, bottomThreshold], //每次刷的范围限制在内部
            ])
            .on("end", updateDate);
          container.select(".brush").remove();
          container.append("g").attr("class", "brush").call(brush);
          // .attr("transform", `translate(0,${this.height - 7})`);

          // index area plot
          container
            .append("path")
            .datum(d[1].sci)
            .style("stroke", "#90A4AE")
            .style("fill", "#90A4AE")
            .style("opacity", 0.5)
            .attr("d", indexArea);
          // stock line plots
          container
            .append("g")
            .selectAll(".stockLine")
            .data(Object.entries(d[1]).filter((d) => d[0] !== "sci")) //过滤后剩下各个选中的股票
            .enter()
            .append("path")
            .attr("class", "stock-line")
            .attr("d", (d) => {
              return stockLine(d[1]);
            })
            .attr("fill", "none")
            .attr("stroke-width", "2px")
            .attr("stroke", "#A1887F");
        });
    },
  },
};
</script>

<style scoped>
</style>
