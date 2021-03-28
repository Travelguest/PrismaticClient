<template>
  <div></div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: "DynamicGraphView",
  components: {},
  props: {
    corrDistribution: Object,
    corrCluster: Object,
  },
  emits: ["clickedYear"],
  data() {
    return {
      svg: null,
      width: 0,
      height: 1175,

      distWidth: 80,
      distHeight: 105,
      distPaddingHeight: 12,
      distPaddingWidth: 20,

      graphMaxNodes: 40,

      color: d3.schemeTableau10,

      yearSelected: "2020",
      correlationRange: [0.6, 1],
      correlationMarks: { 0.6: "0.6", 0: "0", 1: "1" },
      correlatedStocks: [],
    };
  },
  watch: {
    corrDistribution: function () {
      this.svg.selectAll(".dist").remove();
      this.renderDistChart();
    },
    corrCluster: function () {
      this.svg.selectAll(".graph").remove();
      this.renderNodeLink();
    },
    periodRange: function () {
      this.$emit("update-period-range", this.periodRange);
    },
  },
  computed: {},
  mounted: function () {
    console.log("corrDistribution:", this.corrDistribution);
    console.log("corrCluster:", this.corrCluster);
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

      //topNodes:根据betweenness重要性排序后得到的股票代码数组
      let topNodes = Object.fromEntries(
        Object.entries(this.corrCluster).map(([k, v]) => [
          k,
          Object.entries(v.betweenness)
            .sort((a, b) => (a[1] < b[1] ? 1 : -1)) // descending order
            .slice(-this.graphMaxNodes) // select top n
            .map((x) => x[0]) // keep only keys
            .sort((x, y) => v.components[x] - v.components[y]), //再按compoents升序排序
        ])
      );

      console.log("数组：", Object.entries(this.corrCluster));
      console.log("topNodes", topNodes);

      let xScale = Object.fromEntries(
        Object.entries(topNodes).map(([k, v]) => [
          k,
          d3.scalePoint().domain(v).range([10, graphWidth-10]),
        ])
      );

      //graphY : yScale()
      let graphY = d3
        .scalePoint()
        .domain(Object.keys(this.corrCluster).sort().reverse()) //year.reverse()
        .range([
          this.distHeight * 0.75 + 3,
          this.distHeight * 0.75 + 3 + graphHeight * 9,
        ]);

      console.log("xScale", xScale);

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
        .attr("y", this.distPaddingHeight - this.distHeight * 0.75)
        .attr("width", graphWidth)
        .attr("height", graphHeight - this.distPaddingHeight)
        .style("fill", "#D6DBDF")
        .style("opacity", 0.5)
        .on("click", (_, d) => {
          _this.$emit("clickedYear", topNodes[d], d); //结点列表，年份
        });

      //text
      container
        .append("text")
        .attr("x", graphWidth - 115)
        .attr("y", -20)
        .text((d) => d)
        .style("font-size", "48px")
        // .style("stroke","black")
        .style("fill", "white")
        .style("stroke-width", "0.8px")
        .style("font-weight", "700")
        .style("opacity", 1);

      console.log(Object.keys(this.corrCluster).sort().reverse());
      // draw the node link diagram
      //year,index,group...
      container.each((d, i, c) => {
        let container = d3.select(c[i]);
        console.log("each:", d, i, c);

        let last = 0;
        let cnt = [];
        let temp = 0;
        //计算每个族有几个结点
        topNodes[d].forEach((id) => {
          if (this.corrCluster[d].components[id] != last) {
            last = this.corrCluster[d].components[id];
            cnt.push(temp);
            temp = 1; //发现第一个不同的
          } else {
            temp++;
          }
        });
        cnt.push(temp); //最后一组
        console.log("cnt:", cnt);

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

            return xScale[d](topNodes[d][start]) -10 ;
          })
          .attr("y", -20)
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("height", 40)
          .attr("width", (length, i) => {
            let start = 0;
            for (let j in cnt) {
              if (j < i) start += cnt[j]; //不包含自己的长度
            }
            let end = start + length - 1;
            console.log("start,end", start, end);
            console.log(topNodes[d][start], topNodes[d][end]);
            console.log(
              "end,start",
              xScale[d](topNodes[d][end]),
              xScale[d](topNodes[d][start])
            );
            if (start !== end) {
              return xScale[d](topNodes[d][end]) - xScale[d](topNodes[d][start]) + 20;
            } else return 20;
          })
          .style("fill", "none")
          .style("stroke", "#5D83BE")
          .style("stroke-width", 1);

        // draw the xAxis
        container
          .append("g")
          .attr("class", "xAxis")
          .call(d3.axisBottom(xScale[d]))
        .call((g) => g.selectAll(".tick").remove());

        // draw node to the axis
        container
          .selectAll(".node")
          .data(topNodes[d])
          .enter()
          .append("circle")
          .attr("class", "node")
          .attr("id", (node) => node)
          .attr("cx", (node) => xScale[d](node))
          .attr("r", "4px")
          .style("fill", "cornflowerblue");

        // draw a vertical line to link the same node in last year
        if (i !== 0) {
          let lastD = "" + (2021 - i);
          container
            .selectAll(".linkage")
            .data(topNodes[d].filter((x) => topNodes[lastD].includes(x))) //上一年出现过该股票
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
            .attr("stroke", "cornflowerblue")
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
              g.selectAll(".tick text").attr("dx", 0).attr("dy", 0);
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
          let brush = d3
            .brushY()
            .extent([
              [_this.distWidth, 0],
              [_this.distWidth + 32, _this.distHeight],
            ])
            .on("end", this.updateDate);
          container.select(".brush").remove();
          container.append("g").attr("class", "brush").call(brush);
          // .attr("transform", `translate(0,${this.height - 7})`);

          // index area plot
          container
            .append("path")
            .datum(d[1].sci)
            .style("stroke", "rgba(80,161,255,0.10)")
            .style("fill", "rgba(80,161,255,0.10)")
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
            .attr("stroke", "cornflowerblue");
        });
    },
    updateDate({ selection }) {
      if (selection) {
        let distY = d3
          .scaleLinear()
          .domain([1, -0.5])
          .range([0, this.distHeight]);
        let start = distY.invert(selection[0]);
        let end = distY.invert(selection[1]);
        // .toISOString().slice(0, 10);
        if (start !== end) {
          console.log("start,end:", start, end);
          // this.$emit("updateBrush", start, end, this.title);
        }
      }
    },
  },
};
</script>

<style scoped>
</style>
