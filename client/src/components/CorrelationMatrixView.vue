<template>
  <div>
    <div id="knowledge_graph_title">Correlation Matrix</div>
    <div id="triangle"></div>
    <div id="matrix" style="height: 100%; width: 100%"></div>
    <a-range-picker
        id="date-picker"
        v-model:value="periodRange"
        :disabledDate="periodDisabledRange"
        :ranges="periodPresetRange"
        :size="'small'"
        :format="'MM/YY'"
        :allowClear="false"
    />
    <!--    <draggable-->
    <!--        :list="matrixColumn"-->
    <!--        :disabled="!enabled"-->
    <!--        class="testClass"-->
    <!--        item-key="name"-->
    <!--        ghost-class="ghost"-->
    <!--        :move="checkMove"-->
    <!--        @start="dragging = true"-->
    <!--        @end="dragging = false"-->
    <!--    >-->
    <!--      <template #item="{ element }">-->
    <!--        <div class="list-group-item" :class="{ 'not-draggable': !enabled }">-->
    <!--          {{ element }}-->
    <!--        </div>-->
    <!--      </template>-->
    <!--    </draggable>-->
  </div>
</template>

<script>
import _ from "lodash";
import * as d3 from "d3";
import moment from "moment";
import 'moment/dist/locale/zh-cn';
// import draggable from "vuedraggable";

export default {
  name: "CorrelationMatrixView",
  components: {
    // draggable,
  },
  props: {
    selectedYear: String,
    correlationMatrix: Object,
    correlationReturn: Object,
  },
  emits: ["selectedStockFromMatrix", "update-period-range"],
  computed: {
    matrixCorr() {
      return !_.isEmpty(this.correlationMatrix)
          ? this.correlationMatrix.corr
          : [];
    },
    matrixColumn() {
      return !_.isEmpty(this.correlationMatrix)
          ? this.correlationMatrix.columns
          : [];
    },
  },
  data() {
    return {
      svg: null,
      heatmapContainer: null,
      width: 759,
      height: 599,
      margin: { top: 45, right: 145, bottom: 60, left: 120 },
      padding: 0.1,

      colorScheme: d3.interpolateBrBG,
      // colorScheme: d3.interpolateYlGnBu,
      // colorScheme: d3.interpolateYlGn,
      // colorScheme: d3.interpolateYlOrRd,

      dragging: false,
      enabled: true,

      lineData: [
        { row: "600436", col: "600200", val: -0.00632, type: "vol" },
        { row: "000623", col: "000078", val: 0.07383, type: "vol" },
        { row: "600763", col: "000078", val: -0.15669, type: "vol" },
        { row: "603288", col: "000652", val: -0.13302, type: "vol" },
        { row: "600269", col: "000078", val: -0.06548, type: "vol" },
      ],

      periodRange: [moment.utc('2020-01-01', 'YYYY-MM-DD'), moment.utc('2020-06-30', 'YYYY-MM-DD')],
      periodPresetRange: {
        'All': [moment.utc('2011-01-01', 'YYYY-MM-DD'), moment.utc('2020-12-31', 'YYYY-MM-DD')],
        '3Y': [moment.utc('2018-01-01', 'YYYY-MM-DD'), moment.utc('2020-12-31', 'YYYY-MM-DD')],
        '1Y': [moment.utc('2020-01-01', 'YYYY-MM-DD'), moment.utc('2020-12-31', 'YYYY-MM-DD')],
        '3M': [moment.utc('2020-01-01', 'YYYY-MM-DD'), moment.utc('2020-03-31', 'YYYY-MM-DD')],
      },
      periodDisabledRange: (cur) => { return cur < moment.utc('2011-01-01', 'YYYY-MM-DD') || cur > moment.utc('2020-12-31', 'YYYY-MM-DD')},
    };
  },
  watch: {
    correlationMatrix: function () {
      this.renderMatrix();
    },
    selectedYear: function (year) {
      this.periodRange = [
        moment.utc(`${year}-01-01`, "YYYY-MM-DD"),
        moment.utc(`${year}-12-31`, "YYYY-MM-DD")
      ]
    },
    periodRange: function () {
      this.$emit("update-period-range", this.periodRange);
    },
    correlationReturn: function () {
      this.renderMatrix();
    },
  },
  mounted() {
    this.initMatrix();
    this.renderMatrix();
  },
  methods: {
    initMatrix() {
      this.svg = d3
          .select("#matrix")
          .append("svg")
          .attr("viewBox", [0, 0, this.width, this.height]);

      this.heatmapContainer = this.svg
          .append("g")
          .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

      // legend scale
      let legendWidth = 100;
      let legendHeight = 10;
      let legend = this.svg
          .append("g")
          .attr("transform", `translate(${this.width-legendWidth*2.5},${this.margin.top-legendHeight*1.5})`);
      let colorScale = d3.scaleSequential().domain([-1, 1]).interpolator(this.colorScheme);

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
          .data([-1, 1])
          .enter()
          .append("text")
          .attr("y", legendHeight)
          .attr("x", (d) => legendWidth/2 + d*(legendWidth/2+10) )
          .style("text-anchor", "middle")
          .style('font-size', '12')
          .text((d) => d);
    },
    renderMatrix() {
      // Remove all groups in svg
      this.heatmapContainer.selectAll("g").remove();

      let colorScale = d3.scaleSequential().domain([-1, 1]).interpolator(this.colorScheme);
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

      // Heatmap
      this.heatmapContainer
          .append("g")
          .attr("class", "xAxis")
          .call(d3.axisBottom(x).tickSizeOuter(0))
          .attr("transform", `translate(0,${this.height - this.margin.bottom - this.margin.top})`)
          .selectAll(".tick text")
          .attr("transform", "rotate(15)");

      this.heatmapContainer
          .append("g")
          .attr("class", "yAxis")
          .call(d3.axisRight(y).tickSizeOuter(0))
          .attr("transform", `translate(${this.width - this.margin.right - this.margin.left},0)`);


      let cells = this.heatmapContainer
          .selectAll('.cell')
          .data(this.matrixCorr)
          .enter()
          .append('g')
          .attr("class", "cell")
          .attr("transform", d => `translate(${x(d.col)+x.bandwidth()/2},${y(d.row)+y.bandwidth()/2})`);

      let dx = x.bandwidth()/2;
      let dy = y.bandwidth()/2;
      let w = x.bandwidth();
      let h = y.bandwidth();
      // draw rectangles
      cells.filter((d) => d.col !== d.row)
          .append("rect")
          .attr("class", "cell")
          .attr("x", -dx)
          .attr("y", -dy)
          .attr("width", w)
          .attr("height", h)
          .style("fill", (d) => colorScale(d.val))
      // .style("stroke", (d) => colorScale(Math.sign(d.val)*0.9))
      // .style("stroke-width", 1);

      // draw upper frame
      cells.filter((d) => d.col !== d.row && d.type === 'price')
          .append('path')
          .attr("d", `M ${0} ${-dy} L ${dx} ${-dy} L ${dx/1.3} ${-dy/1.3} L ${dx/3} ${-dy/1.3} Z`)
          .attr("fill", d => colorScale(Math.sign(d.val)*0.75));
      cells.filter((d) => d.col !== d.row && d.type === 'price')
          .append('path')
          .attr("d", `M ${dx} ${-dy} L ${dx} ${0} L ${dx/1.3} ${-dy/3} L ${dx/1.3} ${-dy/1.3} Z`)
          .attr("fill", d => colorScale(Math.sign(d.val)*0.5));
      // draw lower frame
      cells.filter((d) => d.col !== d.row && d.type === 'vol')
          .append('path')
          .attr("d", `M ${0} ${dy} L ${-dx} ${dy} L ${-dx/1.3} ${dy/1.3} L ${-dx/3} ${dy/1.3} Z`)
          .attr("fill", d => colorScale(Math.sign(d.val)*0.75));
      cells.filter((d) => d.col !== d.row && d.type === 'vol')
          .append('path')
          .attr("d", `M ${-dx} ${dy} L ${-dx} ${0} L ${-dx/1.3} ${dy/3} L ${-dx/1.3} ${dy/1.3} Z`)
          .attr("fill", d => colorScale(Math.sign(d.val)*0.5));

      // // draw upper triangle
      // cells.filter((d) => d.col !== d.row && d.type === 'price')
      //     .append('path')
      //     .attr("d", `M ${dx/3} ${-dy} L ${dx} ${-dy} L ${dx} ${-dy/3} Z`)
      //     .attr("fill", d => colorScale(Math.sign(d.val)*0.5));
      // cells.filter((d) => d.col !== d.row && d.type === 'price')
      //     .append('path')
      //     .attr("d", `M ${-dx} ${dy/3} L ${-dx} ${dy} L ${-dx/3} ${dy} Z`)
      //     .attr("fill", d => colorScale(Math.sign(d.val)*0.75));
      // // draw lower triangle
      // cells.filter((d) => d.col !== d.row && d.type === 'vol')
      //     .append('path')
      //     .attr("d", `M ${-dx} ${dy/3} L ${-dx} ${dy} L ${-dx/3} ${dy} Z`)
      //     .attr("fill", d => colorScale(Math.sign(d.val)*0.5));
      // cells.filter((d) => d.col !== d.row && d.type === 'vol')
      //     .append('path')
      //     .attr("d", `M ${dx/3} ${-dy} L ${dx} ${-dy} L ${dx} ${-dy/3} Z`)
      //     .attr("fill", d => colorScale(Math.sign(d.val)*0.75));

      // draw diagonal
      let arc = d3.arc()
          .startAngle(d => d[0])
          .endAngle(d => d[1])
          .innerRadius(x.bandwidth()/4)
          .outerRadius(x.bandwidth()/2.4)
          .cornerRadius(5);
      cells.filter((d) => d.col === d.row)
          .append("circle")
          .attr("r", dx)
          .style("fill", (d) => colorScale(Math.sign(d.val)*0.15));
      cells.filter((d) => d.col === d.row)
          .selectAll('.cell')
          .data((d) => [
            [0, Math.abs(d.val)*Math.PI*2, Math.sign(d.val)],
            [Math.abs(d.val)*Math.PI*2, Math.PI*2, Math.sign(d.val)]
          ])
          .enter()
          .append('path')
          .attr("d", arc)
          .attr("fill", (d, i) => i === 0? colorScale(d[2]*0.75): "white");

      let mouseover = function (_, d) {
        d3.selectAll(".cell")
            .filter((k) => !(k.col === d.col || k.row === d.row)) // when not in the same row or column
            .style("opacity", 0.3)
            .style("stroke-width", 0);
        d3.selectAll(".cell")
            .filter((k) => (k.col === d.col || k.row === d.row)) // when in the same row or column
            .style("stroke-width", 1)
            .style("stroke-dasharray", (d) => (d.type === "vol")? "2 2": "0")
            .filter((k) => k.col === k.row) // when in the same row or column
            .style("stroke-width", 0);
      };

      let mouseout = function () {
        d3.selectAll(".cell")
            .style("opacity", 1)
            .style("stroke-width", 0);
      };

      // Heatmap interaction
      d3.selectAll(".cell")
          .on("mouseover", mouseover)
          .on("mouseout", mouseout)
          .on("click", (_, d) => {
            this.$emit("selectedStockFromMatrix", d.row, d.col);
          });

      //barChart
      let xScale = d3
          .scaleLinear()
          .domain(d3.extent(this.correlationReturn, (d) => d.val))
          .range([this.margin.left/3, 0])
          .nice();

      this.heatmapContainer
          .selectAll(".bar")
          .data(this.correlationReturn)
          .enter()
          .append("rect")
          .attr("class", "bar")
          .attr("x", (d) => xScale(d.val))
          .attr("y", (d) => y(d.row))
          .attr("width", (d) => Math.abs(xScale(d.val) - xScale(0)))
          .attr("height", y.bandwidth())
          .style("fill", (d) => (d.val < 0)? "#C65A21": "#407FB4")
          .attr("transform", `translate(${-this.margin.left},0)`);
    },
  },
};
</script>


<style scoped>
.draggableList{
  position:absolute;
  top:550px;
  right:80px;
}
.list-group-item {
  display: inline;
  /* position: relative; */
  width: 50px;
  height: 20px;
  line-height: 3px;
  font-size: 3px;
  background: #777;
  color: #fcfcfc;
  margin: 4px;

  /* display: flex; */
  top: 0px;
  font-weight: bold;
}
.flip-list-move {
  transition: transform 0.5s;
}
.no-move {
  transition: transform 0s;
}
.ghost {
  opacity: 0.5;
  background: #c8ebfb;
}
.list-group {
  min-height: 20px;
}
.list-group-item {
  cursor: move;
}
.list-group-item i {
  cursor: pointer;
}
#knowledge_graph_title {
  position: absolute;
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
#triangle {
  position: absolute;
  top: 0;
  right: 49%;
  border-top: 40px solid #777;
  border-right: 45px solid #ffffff;
  border-bottom: 3px solid #ffff;
}
#matrix {
  position: absolute;
  top: 0;
}
#date-picker {
  position: absolute;
  bottom: 40px;
  left: 5px;
  width: 115px;
}
</style>