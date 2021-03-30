<template>
  <div id="knowledge-graph-container">
    <div id="knowledge-graph-tooltip"></div>
    <a-spin size="large" style="margin-top: 50%;" v-if="isLoading" />
    <svg
      :viewbox="`0 0 ${width} ${height}`"
      :width="width"
      :height="height"
      v-if="!isLoading"
    >
      <defs>
        <linearGradient
          v-for="(d, i) in linkData"
          :key="i"
          :id="`linkGrad-${i}`"
          gradientUnits="userSpaceOnUse"
          v-bind="graidentStart"
          :x2="ribbonRadius * Math.cos(getAngle(d))"
          :y2="ribbonRadius * Math.sin(getAngle(d))"
        >
          <stop offset="0%" :stop-color="colorScale[source.type]"></stop>
          <stop offset="45%" stop-color="#fff"></stop>
          <stop offset="55%" stop-color="#fff"></stop>
          <stop offset="100%" :stop-color="d.color"></stop>
        </linearGradient>
      </defs>

      <filter id="blur">
        <feGaussianBlur stdDeviation="5" />
      </filter>

      <g :transform="`translate(${width / 2}, ${height / 2})`">
        <circle
          v-for="i in 6"
          :key="i"
          cx="0"
          cy="0"
          :r="stockScale(i - 1)"
          fill="none"
          stroke="#d8d8d8"
          :id="i"
        />

        <g>
          <path
            v-for="(d, i) in linkData"
            :key="i"
            :d="ribbon(d)"
            :fill="`url(#linkGrad-${i})`"
            :stroke="d.stocks.has(highlightStock) ? '#333' : '#eee'"
            opacity="0.5"
          />
        </g>

        <g v-for="d in arcs" :key="d.data.name">
          <path
            :d="arc(d)"
            :fill="colorScale[d.data.name]"
            :id="d.data.name"
            opacity="0.5"
          />
          <!-- <text
          :x="Math.cos(d.startAngle+ (d.endAngle-d.startAngle)/2)*240"
          :y="Math.sin(d.startAngle+ (d.endAngle-d.startAngle)/2)*240"
          text-anchor="middle"
        >
          {{d.data.name}}
        </text> -->
        </g>

        <path
          fill="#fff"
          stroke="#777"
          :d="
            `M 0, ${-triangleRadius} 
          L${(1.732 * triangleRadius) / 2},${triangleRadius / 2} 
          L${(-1.732 * triangleRadius) / 2},${triangleRadius / 2} Z `
          "
        />
        <path
          fill="#fefefe"
          fill-opacity="1"
          stroke="#777"
          :d="
            `M 0, ${-triangleRadius} 
          L${(1.732 * triangleRadius) / 2},${triangleRadius / 2} 
          L${(-1.732 * triangleRadius) / 2},${triangleRadius / 2} Z `
          "
          filter="url(#blur)"
        />

        <circle cx="0" cy="0" r="10" fill="#efefef" stroke="#aaa" />

        <g :id="stockCode">
          <path
            v-for="d in handledNodes"
            :key="d.name"
            :d="arcOuter(d)"
            :fill="colorScale[d.type]"
            :stroke="colorScale[d.type]"
            :id="d.name"
            @click="clickOuterNode(stockCode, d.type, d.name)"
            @dblclick="dblClickOuterNode(stockCode, d.type, d.name)"
            @mousemove="mouseMoveEvent($event, d.name)"
            @mouseout="mouseOutEvent"
          />
        </g>

        <g>
          <circle
            v-for="(d, i) in stockPos"
            :key="i"
            :type="d.type"
            r="5"
            :cx="d.radius * Math.cos(d.pos)"
            :cy="d.radius * Math.sin(d.pos)"
            fill="#ccc"
            :stroke="highlightStock == d.name ? '#333' : '#ccc'"
            opacity="0.7"
            @click="clickStock(d.name)"
            @dblclick="dblClickStock(d.name)"
            @mousemove="mouseMoveEvent($event, d.name)"
            @mouseout="mouseOutEvent"
          />
        </g>
      </g>
    </svg>
  </div>
</template>

<script>
import * as d3 from "d3";
import DataService from "@/utils/data-service";

const RADIUS_PADDING = 15;
const RADIUS_RANGE = 2.09;

const TYPE_DATA = [
  { name: "bussiness", value: 1 },
  { name: "location", value: 1 },
  { name: "people", value: 1 },
];

const childrenHash = {
  bussiness: ["industry", "concept"],
  location: ["city", "province"],
  people: ["investor", "management"],
};

/**
 * 已完成: 点击外圈的点, 请求获得的链接, 绘制出相应的股票的点;
 *  点击表示股票的点, 高亮/取消高亮相应的股票和弦;
 *
 * 待完成: 弦的显示效果, 感觉可以再调整一下;
 *  股票的位置编码, 现在是[0,5], 需要根据位置调整;
 *  默认选择的股票, 现在是硬编码的. 再KnowledgeGraphView组件中;
 *    以及处理没有数据时, 比如中间的圆点隐藏掉
 */

export default {
  name: "KnowledgeGraph",
  props: {
    isLoading: Boolean,
    rawData: Object,
    stockCode: String,
  },
  emits: ["addLabel", "addStock"],
  data() {
    return {
      width: 550,
      height: 550,
      margin: {
        left: 10,
        top: 10,
        right: 10,
        bottom: 10,
      },
      triangleRadius: 80,
      colorScale: {
        bussiness: "#3E2D59",//"#44930F",
        industry: "#7D5BB2",//"#69BC71",
        concept: "#BEADD8",//"#69BC9A",

        people: "#592D33",//"#B1ABD5",//"#1a589c",
        investor: "#D8ADB2",//"#6D77BE",//"#5C83B6",
        management: "#B25B65",//"#8B6DBE",//"#5DA7B9",

        location: "#49592D",//"#D5A9D1",//"#81770f",
        city: "#C8D8AD",//"#B46DBE",//"#C8C390",
        province: "#91B25B",//"#BE6D9F",//"#A3AE92",
      },
      // link的终点数组
      linkData: [
        // {startAngle: 4.1887902047863905, endAngle: 4.198246826836389},
      ],
      // 处理后的外圈的圆弧
      handledNodes: [],
      // key：(type: city等， name: 具体条目): value: 在handledNodes中的下标
      nodeDict: {},
      // link的起点
      source: { startAngle: 0, endAngle: 0.13277789797532066, type: "city" },
      // 股票的位置数组
      stockPos: [],
      highlightStock: null,
    };
  },
  mounted() {
    if (this.rawData) this.handledData(this.rawData);
  },
  computed: {
    stockScale() {
      return d3
        .scaleLinear()
        .domain([0, 5])
        .clamp(true)
        .range([
          this.chartWidth / 2 - 4.1 * RADIUS_PADDING,
          this.triangleRadius,
        ]);
    },

    chartWidth() {
      return this.width - this.margin.left - this.margin.right;
    },

    chartHeight() {
      return this.height - this.margin.top - this.margin.bottom;
    },

    arc() {
      return (
        d3
          .arc()
          .innerRadius(this.chartWidth / 2 - 4 * RADIUS_PADDING)
          .outerRadius(this.chartWidth / 2 - 3 * RADIUS_PADDING)
          // .innerRadius(this.chartWidth/2 - 2.5*RADIUS_PADDING)
          // .outerRadius(this.chartWidth /2- 0.5*RADIUS_PADDING)
          .padAngle(0.01)
      );
    },

    arcOuter() {
      return d3
        .arc()
        .innerRadius(this.chartWidth / 2 - 2.5 * RADIUS_PADDING)
        .outerRadius(this.chartWidth / 2 - RADIUS_PADDING)
        .padAngle(0.01)
        .cornerRadius(6);
    },

    arcs() {
      return d3
        .pie()
        .padAngle(0.01)
        .sort(null)
        .value((d) => d.value)(TYPE_DATA);
    },

    ribbonRadius() {
      return this.chartWidth / 2 - 3 * RADIUS_PADDING;
    },

    ribbon() {
      return d3
        .ribbon()
        .radius(this.ribbonRadius)
        .source(() => this.source)
        .target((d) => d)
        .padAngle(0.01);
    },

    graidentStart() {
      const angle = this.getAngle(this.source);

      return {
        x1: this.ribbonRadius * Math.cos(angle),
        y1: this.ribbonRadius * Math.sin(angle),
      };
    },
  },

  watch: {
    rawData(newValue) {
      this.handledData(newValue);
    },
  },

  methods: {
    getAngle(d) {
      const { startAngle, endAngle } = d;
      if (startAngle && endAngle) {
        return (endAngle - startAngle) / 2 + startAngle - Math.PI / 2;
      }
      return 0;
    },

    clickStock(name) {
      if (this.highlightStock === name) {
        this.highlightStock = null;
      } else {
        this.highlightStock = name;
      }
    },
    clickOuterNode(code, type, name) {
      DataService.post(
        // TODO 还没有对接传过来的stockCode
        "get_knowledge_graph_links",
        [code, type, name],
        (res) => {
          // {source, target}
          let endNodes = {};
          const resKeys = Object.keys(res);
          const counts = resKeys.map((stock) => {
            const propertyOfStock = res[stock];

            // 分类型统计数量
            const countByType = TYPE_DATA.map(({ name }) => {
              let count = 0;

              childrenHash[name].forEach((hashKey) => {
                if (propertyOfStock[hashKey]) {
                  propertyOfStock[hashKey].forEach((property) => {
                    const dictKey = hashKey + "-" + property;
                    if (this.nodeDict[dictKey]) {
                      count++;
                      // endNodes.add(dictKey);
                      if (!endNodes[dictKey]) {
                        endNodes[dictKey] = new Set();
                      }
                      endNodes[dictKey].add(stock);
                    }
                  });
                }
              });

              return count;
            });

            return countByType;
          });

          // 120度的圆弧
          const radiusScale = d3
            .scaleLinear()
            .domain([0, resKeys.length - 1])
            .range([0, RADIUS_RANGE]);

          this.linkData = Object.keys(endNodes).map((d) => {
            const { startAngle, endAngle, type } = this.handledNodes[
              this.nodeDict[d]
            ];
            return {
              startAngle,
              endAngle,
              stocks: endNodes[d],
              color: this.colorScale[type],
            };
          });

          let stockPos = [];
          counts.forEach((count, i) => {
            count.forEach((countValue, typeIndex) => {
              if (countValue) {
                stockPos.push({
                  name: resKeys[i],
                  // 点放的角度
                  pos: radiusScale(i) + typeIndex * RADIUS_RANGE - 3.14 / 2,
                  // 点的半径
                  radius: this.stockScale(countValue),
                  type: TYPE_DATA[typeIndex].name,
                });
              }
            });
          });

          this.stockPos = stockPos;
          this.source = this.handledNodes[this.nodeDict[type + "-" + name]];
        }
      );
    },

    mouseMoveEvent(event, attrs) {
      // console.log(event, attrs);
      d3.select("#knowledge-graph-tooltip")
        .style("left", event.offsetX + 10 + "px")
        .style("top", event.offsetY + 10 + "px")
        .style("display", "block")
        .html(attrs);
    },

    mouseOutEvent() {
      d3.select("#knowledge-graph-tooltip").style("display", "none");
    },

    dblClickOuterNode(code, type, name) {
      // console.log(code, type, name);
      this.$emit("addLabel", type, name);
    },

    dblClickStock(code) {
      // console.log(code);
      this.$emit("addStock", code);
    },

    handledData(datum) {
      // console.log(this.arcs)
      let arr = [];
      let dict = {};

      this.arcs.forEach(({ data, endAngle, startAngle }) => {
        const name = data.name;

        let res = 0;
        childrenHash[name].forEach((name) => {
          const node = datum[name];
          if (node) {
            const sum = Object.values(node).reduce(
              (a, b) => a + 1 / Math.log(b + 1),
              0
            );
            res += sum;
          }
        });

        const radiusScale = d3
          .scaleLinear()
          .domain([0, res])
          .range([0, endAngle - startAngle]);
        let beginAngle = startAngle;
        childrenHash[name].forEach((name) => {
          const node = datum[name];
          node &&
            Object.keys(node).forEach((key) => {
              const duration = radiusScale(1 / Math.log(node[key] + 1));
              dict[name + "-" + key] = arr.length;

              arr.push({
                type: name,
                name: key,
                startAngle: beginAngle,
                endAngle: (beginAngle += duration),
              });
            });
        });
      });

      this.handledNodes = arr;
      this.nodeDict = dict;
    },
  },
};
</script>

<style scoped>
#knowledge-graph-container {
  position: relative;
  width: 550px;
  height: 550px;
}

#knowledge-graph-tooltip {
  position: absolute;
  display: none;
  opacity: 0.8;
  width: fit-content;
  height: fit-content;
  background-color: #ffffff;
  border: 1px solid #999999;
  border-radius: 2px;
  pointer-events: none;
  padding: 10px;
  z-index: 99;
  -webkit-user-select: none;
}

circle {
  transition: stroke 300ms ease-in-out;
  cursor: pointer;
}
</style>
