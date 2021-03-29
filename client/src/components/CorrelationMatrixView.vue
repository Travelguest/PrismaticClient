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
    <draggable
      id="drag-area-bottom"
      :list="curMatrixColumn"
      item-key="name"
      forceFallback="true"
      :options="{ animation: 1000, ghostClass: 'ghost' }"
      @end="dragEnd"
    >
      <template #item="{ element}">
        <a-tag
          color="red"
          class="drag-item-bottom"
          :key="element"
          :style="{
            position: 'absolute',
            left: rectXScale(element) - 15 + rectWidth / 2 + 'px',
          }"
          @dblclick="removeColumn(element)"
        >
          <text :id="element">{{ element }}</text>
        </a-tag>
      </template>
    </draggable>
    <draggable
      id="drag-area-right"
      :list="curMatrixColumn"
      item-key="name"
      forceFallback="true"
      :options="{ animation: 1000, ghostClass: 'ghost' }"
      @end="dragEnd"
    >
      <template #item="{ element}">
        <a-tag
          color="red"
          class="drag-item-right"
          :key="element"
          :style="{
            position: 'absolute',
            top: rectYScale(element) - 10 + rectWidth / 2 + 'px',
          }"
          @dblclick="removeColumn(element)"
        >
          <text :id="element">{{ element }}</text>
        </a-tag>
      </template>
    </draggable>
    <!-- <div id="del-btns">
      <svg
        class="icon"
        aria-hidden="true"
        :style="{
          cursor: 'pointer',
          position: 'absolute',
          left: rectXScale(item) - 14 + rectWidth / 2 + 'px',
        }"
        :key="item"
        v-for="item in curMatrixColumn"
        @click="removeColumn(item)"
      >
        <use xlink:href="#iconbaseline-close-px"></use>
      </svg>
    </div> -->
    <div id="upset"></div>
  </div>
</template>

<script>
import _ from "lodash";
import * as d3 from "d3";
import moment from "moment";
import "moment/dist/locale/zh-cn";
import draggable from "vuedraggable";

export default {
  name: "CorrelationMatrixView",
  components: {
    draggable,
  },
  props: {
    selectedYear: String,
    correlationMatrix: Object,
    correlationReturn: Object,
    labelToStockCode: Object,
    selectLabels: Object,
  },
  emits: [
    "selectedStockFromMatrix",
    "update-period-range",
    "remove-stock-from-matrix",
    "delLabel",
  ],
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
    rectXScale() {
      return d3
        .scaleBand()
        .domain(this.curMatrixColumn)
        .padding(this.padding)
        .range([0, this.width - this.margin.right - this.margin.left]);
    },
    rectYScale() {
      return d3
        .scaleBand()
        .domain(this.curMatrixColumn)
        .padding(this.padding)
        .range([0, this.height - this.margin.bottom - this.margin.top]);
    },
    upsetXScale() {
      return d3
        .scaleBand()
        .domain(this.labels)
        .padding(this.padding)
        .range([
          this.upsetMargin.left,
          this.upsetWidth - this.upsetMargin.right,
        ]);
    },
  },
  data() {
    return {
      svg: null,
      heatmapContainer: null,
      width: 874,
      height: 600,
      margin: { top: 45, right: 280, bottom: 60, left: 115 },
      padding: 0.1,

      // upset attrs
      upsetSvg: null,
      upsetWidth: 250,
      upsetHeight: 600,
      upsetMargin: { top: 45, right: 10, left: 15, bottom: 60 },
      labels: ["", "", "", "", ""],

      colorScheme: d3.interpolateBrBG,
      // colorScheme: d3.interpolateYlGnBu,
      // colorScheme: d3.interpolateYlGn,
      // colorScheme: d3.interpolateYlOrRd,

      dragging: false,
      enabled: true,

      curMatrixColumn: [],
      rectWidth: 0,

      periodRange: [
        moment.utc("2020-01-01", "YYYY-MM-DD"),
        moment.utc("2020-06-30", "YYYY-MM-DD"),
      ],
      periodPresetRange: {
        All: [
          moment.utc("2011-01-01", "YYYY-MM-DD"),
          moment.utc("2020-12-31", "YYYY-MM-DD"),
        ],
        "3Y": [
          moment.utc("2018-01-01", "YYYY-MM-DD"),
          moment.utc("2020-12-31", "YYYY-MM-DD"),
        ],
        "1Y": [
          moment.utc("2020-01-01", "YYYY-MM-DD"),
          moment.utc("2020-12-31", "YYYY-MM-DD"),
        ],
        "3M": [
          moment.utc("2020-01-01", "YYYY-MM-DD"),
          moment.utc("2020-03-31", "YYYY-MM-DD"),
        ],
      },
      periodDisabledRange: (cur) => {
        return (
          cur < moment.utc("2011-01-01", "YYYY-MM-DD") ||
          cur > moment.utc("2020-12-31", "YYYY-MM-DD")
        );
      },
    };
  },
  watch: {
    correlationMatrix: function() {
      this.curMatrixColumn = this.matrixColumn;
      this.renderMatrix();
    },
    selectedYear: function(year) {
      this.periodRange = [
        moment.utc(`${year}-01-01`, "YYYY-MM-DD"),
        moment.utc(`${year}-12-31`, "YYYY-MM-DD"),
      ];
    },
    periodRange: function() {
      this.$emit("update-period-range", this.periodRange);
    },
    // correlationReturn: function() {
    //   this.curMatrixColumn = this.matrixColumn;
    // },
    labelToStockCode() {
      this.labels = this.selectLabels;
      this.renderMatrix();
    },
  },
  mounted() {
    this.initMatrix();
    this.renderMatrix();
  },
  methods: {
    initMatrix() {
      this.curMatrixColumn = this.matrixColumn;

      this.svg = d3
        .select("#matrix")
        .append("svg")
        .attr("viewBox", [0, 0, this.width, this.height]);

      this.heatmapContainer = this.svg
        .append("g")
        .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

      let defs = this.svg.append("defs");
      defs
        .append("pattern")
        .attr("id", `pattern_stripe`)
        .attr("width", 4)
        .attr("height", 4)
        .attr("patternUnits", "userSpaceOnUse")
        .attr("patternTransform", "rotate(45)")
        .append("rect")
        .attr("width", 2)
        .attr("height", 4)
        .attr("transform", "translate(0, 0)")
        .attr("fill", "white");
      defs
        .append("mask")
        .attr("id", `mask_stripe`)
        .append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("fill", `url(#pattern_stripe)`)
        .attr("stroke", "black");

      // legend scale
      let legendWidth = 100;
      let legendHeight = 10;
      let legend = this.svg
        .append("g")
        .attr(
          "transform",
          `translate(${this.width - legendWidth * 4.5},${this.margin.top -
            legendHeight * 2.5})`
        );
      let colorScale = d3
        .scaleSequential()
        .domain([-1, 1])
        .interpolator(this.colorScheme);

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
        .attr("x", (d) => legendWidth / 2 + d * (legendWidth / 2 + 10))
        .style("text-anchor", "middle")
        .style("font-size", "12")
        .text((d) => d);

      // legend triangle
      let legendTriangle = this.svg
        .append("g")
        .attr("transform", `translate(580, 15)`);
      legendTriangle
        .append("path")
        .attr("d", `M 0 0 h 20 l -4 4 h -12 Z`)
        .attr("fill", colorScale(0.75));
      legendTriangle
        .append("path")
        .attr("d", `M 20 0 v 20 l -4 -4 v -12 Z`)
        .attr("fill", colorScale(0.5));
      legendTriangle
        .append("path")
        .attr("d", `M 0 0 v 20 l 4 -4 v -12 Z`)
        .attr("fill", colorScale(-0.5));
      legendTriangle
        .append("path")
        .attr("d", `M 0 20 h 20 l -4 -4 h -12 Z`)
        .attr("fill", colorScale(-0.75));
      legendTriangle
        .append("text")
        .attr("x", 1)
        .attr("y", -2)
        .style("font-size", "9")
        .text("0.75");
      legendTriangle
        .append("text")
        .attr("x", 21)
        .attr("y", 13)
        .style("font-size", "9")
        .text("0.5");
      legendTriangle
        .append("text")
        .attr("x", -1)
        .attr("y", 29)
        .style("font-size", "9")
        .text("-0.75");
      legendTriangle
        .append("text")
        .attr("x", -17)
        .attr("y", 13)
        .style("font-size", "9")
        .text("-0.5");
      legendTriangle
        .append("text")
        .attr("x", 25)
        .attr("y", 0)
        .style("font-size", "10")
        .text("Price");
      legendTriangle
        .append("text")
        .attr("x", -37)
        .attr("y", 26)
        .style("font-size", "10")
        .text("Volume");

      // upset
      this.upsetSvg = d3
        .select("#upset")
        .append("svg")
        .attr("viewBox", [0, 0, this.upsetWidth, this.upsetHeight]);
    },
    renderMatrix() {
      // Remove all groups in svg
      this.heatmapContainer.selectAll("g").remove();
      this.heatmapContainer.selectAll("rect").remove();
      this.upsetSvg.selectAll("g").remove();

      let colorScale = d3
        .scaleSequential()
        .domain([-1, 1])
        .interpolator(this.colorScheme);

      // Heatmap
      this.heatmapContainer
        .append("g")
        .attr("class", "xAxis")
        .call(d3.axisBottom(this.rectXScale).tickSizeOuter(0))
        .attr(
          "transform",
          `translate(0,${this.height - this.margin.bottom - this.margin.top})`
        )
        .selectAll(".tick text")
        .attr("transform", "rotate(45)");

      this.heatmapContainer
        .append("g")
        .attr("class", "yAxis")
        .call(d3.axisRight(this.rectYScale).tickSizeOuter(0))
        .attr(
          "transform",
          `translate(${this.width - this.margin.right - this.margin.left},0)`
        );

      // use divs to implement dragging
      // so remove texts here
      this.heatmapContainer
        .select(".xAxis")
        .selectAll("text")
        .remove();
      this.heatmapContainer
        .select(".yAxis")
        .selectAll("text")
        .remove();

      let cells = this.heatmapContainer
        .selectAll(".cell")
        .data(this.matrixCorr)
        .enter()
        .append("g")
        .attr("class", "cell")
        .attr(
          "transform",
          (d) =>
            `translate(${this.rectXScale(d.col) +
              this.rectXScale.bandwidth() / 2},${this.rectYScale(d.row) +
              this.rectYScale.bandwidth() / 2})`
        );

      let dx = this.rectXScale.bandwidth() / 2;
      let dy = this.rectYScale.bandwidth() / 2;
      let w = this.rectXScale.bandwidth();
      let h = this.rectYScale.bandwidth();

      this.rectWidth = this.rectXScale.bandwidth();

      // update width of draggable divs
      this.$nextTick(function() {
        d3.selectAll(".drag-item-bottom").style("width", w / 3);
      });

      // draw rectangles
      cells
        .filter((d) => d.col !== d.row)
        .append("rect")
        .attr("class", "cell")
        .attr("x", -dx)
        .attr("y", -dy)
        .attr("width", w)
        .attr("height", h)
        .style("fill", (d) => colorScale(d.val));
      // .style("stroke", (d) => colorScale(Math.sign(d.val)*0.9))
      // .style("stroke-width", 1);

      // draw upper frame
      cells
        .filter((d) => d.col !== d.row && d.type === "price")
        .append("path")
        .attr(
          "d",
          `M ${0} ${-dy} L ${dx} ${-dy} L ${dx / 1.3} ${-dy / 1.3} L ${dx /
            3} ${-dy / 1.3} Z`
        )
        .attr("fill", (d) => colorScale(Math.sign(d.val) * 0.75));
      cells
        .filter((d) => d.col !== d.row && d.type === "price")
        .append("path")
        .attr(
          "d",
          `M ${dx} ${-dy} L ${dx} ${0} L ${dx / 1.3} ${-dy / 3} L ${dx /
            1.3} ${-dy / 1.3} Z`
        )
        .attr("fill", (d) => colorScale(Math.sign(d.val) * 0.5));
      // draw lower frame
      cells
        .filter((d) => d.col !== d.row && d.type === "vol")
        .append("path")
        .attr(
          "d",
          `M ${0} ${dy} L ${-dx} ${dy} L ${-dx / 1.3} ${dy / 1.3} L ${-dx /
            3} ${dy / 1.3} Z`
        )
        .attr("fill", (d) => colorScale(Math.sign(d.val) * 0.75));
      cells
        .filter((d) => d.col !== d.row && d.type === "vol")
        .append("path")
        .attr(
          "d",
          `M ${-dx} ${dy} L ${-dx} ${0} L ${-dx / 1.3} ${dy / 3} L ${-dx /
            1.3} ${dy / 1.3} Z`
        )
        .attr("fill", (d) => colorScale(Math.sign(d.val) * 0.5));

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
      let arc = d3
        .arc()
        .startAngle((d) => d[0])
        .endAngle((d) => d[1])
        .innerRadius(this.rectXScale.bandwidth() / 4)
        .outerRadius(this.rectXScale.bandwidth() / 2.4)
        .cornerRadius(5);
      cells
        .filter((d) => d.col === d.row)
        .append("circle")
        .attr("r", dx)
        .style("fill", (d) => colorScale(Math.sign(d.val) * 0.15));
      cells
        .filter((d) => d.col === d.row)
        .selectAll(".cell")
        .data((d) => [
          [0, Math.abs(d.val) * Math.PI * 2, Math.sign(d.val)],
          [Math.abs(d.val) * Math.PI * 2, Math.PI * 2, Math.sign(d.val)],
        ])
        .enter()
        .append("path")
        .attr("d", arc)
        .attr("fill", (d, i) => (i === 0 ? colorScale(d[2] * 0.75) : "white"));

      let mouseover = function(_, d) {
        d3.selectAll(".cell")
          .filter((k) => !(k.col === d.col || k.row === d.row)) // when not in the same row or column
          .style("opacity", 0.3)
          .style("transition", "0.8s")
          .style("stroke-width", 0);
        d3.selectAll(".cell")
          .filter((k) => k.col === d.col || k.row === d.row) // when in the same row or column
          .style("stroke-width", 1)
          .style("stroke-dasharray", (d) => (d.type === "vol" ? "2 2" : "0"))
          .filter((k) => k.col === k.row) // when in the same row or column
          .style("stroke-width", 0);
      };

      let mouseout = function() {
        d3.selectAll(".cell")
          .style("opacity", 1)
          .style("transition", "0.8s")
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
      let barchartGroup = this.heatmapContainer
        .append("g")
        .attr("transform", `translate(${-this.margin.left}, 0)`);
      // let returnDomain = d3.extent(this.correlationReturn, (d) => d.val);
      let xScale = d3
        .scaleLinear()
        .domain([0, d3.max(this.correlationReturn, (d) => d.val)])
        .range([this.margin.left - 8, 10]);
      // if (returnDomain[0] >= 1) {
      //   xScale = d3
      //     .scaleLinear()
      //     .domain([1, returnDomain[1]])
      //     .range([this.margin.left / 2, 5]);
      // } else if (returnDomain[1] <= 1) {
      //   xScale = d3
      //     .scaleLinear()
      //     .domain([returnDomain[0], 1])
      //     .range([this.margin.left - 5, this.margin.left / 2]);
      // } else {
      //   xScale = d3
      //     .scaleLinear()
      //     .domain([returnDomain[1], 1, returnDomain[0]])
      //     .range([5, this.margin.left / 2, this.margin.left - 5]);
      // }

      barchartGroup
        .append("g")
        .call(
          d3
            .axisBottom(xScale)
            .tickSizeOuter(0)
            .tickValues([3, 2, 1, 0])
        )
        .attr("transform", `translate(0, 495)`);
      // .selectAll(".tick text")
      // .attr("transform", "rotate(-15)");

      barchartGroup
        .selectAll(".bar")
        .data(this.correlationReturn)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", (d) => xScale(d.val))
        .attr("y", (d) => this.rectYScale(d.row))
        .attr("width", (d) => Math.abs(xScale(d.val) - xScale(0)))
        .attr("height", this.rectYScale.bandwidth())
        .style("mask", "url(#mask_stripe)")
        .style("fill", (d) => (d.val < 1 ? colorScale(-0.5) : colorScale(0.5)));

      // upset
      let tickGroup = this.upsetSvg
        .append("g")
        .attr(
          "transform",
          `translate(${this.upsetMargin.left}, ${this.upsetMargin.top + 500})`
        );
      for (let i = 0; i < 5; i++) {
        // tickGroup
        //   .append("path")
        //   .attr("stroke", "black")
        //   .attr("fill", "none")
        //   .attr("d", `M ${30 * i + 10 * i} 0 h 30`);
        tickGroup
          .append("path")
          .attr("stroke", "black")
          .attr("fill", "none")
          .attr("id", this.labels[i])
          .attr("d", `M ${30 * i + 10 * i} 0 l 35 35`);
        tickGroup
          .append("text")
          .attr("dy", -5)
          .append("textPath")
          .attr("xlink:href", `#${this.labels[i]}`)
          .style("font-size", 10)
          .style("-webkit-user-select", "none")
          .text(
            this.labels[i].length <= 3
              ? this.labels[i]
              : this.labels[i].substring(0, 3)
          )
          .on("dblclick", () => {
            this.$emit("delLabel", i);
          });
      }

      let dotsGroup = this.upsetSvg
        .append("g")
        .attr(
          "transform",
          `translate(${this.upsetMargin.left}, ${this.upsetMargin.top})`
        );
      if (Object.keys(this.labelToStockCode).length !== 0) {
        for (let i = 0; i < 5; i++) {
          if (this.labels[i] in this.labelToStockCode) {
            let curLabelToStockCode = this.labelToStockCode[this.labels[i]];
            let dotsCenter = [];
            for (let j = 0; j < this.curMatrixColumn.length; j++) {
              if (curLabelToStockCode.indexOf(this.curMatrixColumn[j]) !== -1) {
                // add dots
                dotsGroup
                  .append("circle")
                  .attr("cx", 30 * i + 10 * i + 10)
                  .attr(
                    "cy",
                    this.rectYScale(this.curMatrixColumn[j]) +
                      this.rectWidth / 2
                  )
                  .attr("r", this.rectWidth / 4)
                  .style("fill", "cornflowerblue");
                dotsCenter.push(
                  this.rectYScale(this.curMatrixColumn[j]) + this.rectWidth / 2
                );
              }
            }
            // add lines
            for (let k = 0; k < dotsCenter.length - 1; k++) {
              dotsGroup
                .append("path")
                .attr("fill", "none")
                .attr("stroke", "black")
                .attr(
                  "d",
                  `M ${30 * i + 10 * i + 10} ${dotsCenter[k] +
                    this.rectWidth / 4} V ${dotsCenter[k + 1] -
                    this.rectWidth / 4}`
                );
            }
          }
        }
      }
    },
    dragEnd() {
      this.renderMatrix();
    },
    removeColumn(val) {
      this.curMatrixColumn.splice(this.curMatrixColumn.indexOf(val), 1);
      this.$emit("remove-stock-from-matrix", this.curMatrixColumn);
    },
  },
};
</script>

<style scoped>
#knowledge_graph_title {
  position: absolute;
  top: 0;
  padding: 0 20px;
  width: 309.531px;
  height: 40px;
  line-height: 40px;
  font-size: 24px;
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
  left: 309.531px;
  border-top: 40px solid #777;
  border-right: 45px solid #ffffff;
  border-bottom: 3px solid #ffff;
}
#matrix {
  position: absolute;
  top: 0;
  z-index: 0;
}
#date-picker {
  position: absolute;
  top: 10px;
  right: 30px;
  width: 110px;
}
#drag-area-bottom {
  position: absolute;
  display: flex;
  width: 500px;
  height: 13px;
  top: 545px;
  left: 120px;
}
.drag-item-bottom {
  /* background: white; */
  margin-top: 3px !important;
  height: 40px !important;
  width: 20px !important;
  writing-mode: vertical-lr !important;
  cursor: move !important;
  padding: 0 !important;
  transition: none !important;
  -webkit-user-select: none;
}
.drag-item-bottom-ghost {
  opacity: 0.5;
}
.drag-item-bottom text {
  display: inline-block;
  font-size: 12px;
  -webkit-text-size-adjust: none;
  -webkit-transform: scale(0.83, 0.83);
  transform: scale(0.83, 0.83);
}
#drag-area-right {
  position: absolute;
  width: 40px;
  height: 500px;
  top: 45px;
  left: 582px;
}
.drag-item-right {
  margin-left: 3px !important;
  height: 20px !important;
  width: 45px !important;
  cursor: move !important;
  padding: 0 !important;
  transition: none !important;
  -webkit-user-select: none;
}
#del-btns {
  position: absolute;
  display: flex;
  width: 500px;
  top: 585px;
  left: 123px;
}
#upset {
  position: absolute;
  left: 650px;
  width: 250px;
  height: 100%;
  /* background: rgba(214, 219, 223, 0.5); */
}
</style>
