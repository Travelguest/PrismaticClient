<template>
  <svg :viewbox="`0 0 ${width} ${height}`" :width="width" :height="height">
    <filter id="blur">
      <feGaussianBlur stdDeviation="5"/>
    </filter>
    <g :transform="`translate(${width/2}, ${height/2})`">
      <circle 
        v-for="i in 6"
        :key="i"
        cx="0" cy="0"
        :r="stockScale(i-1)"
        fill="none" stroke="#d8d8d8"
        :id="i"
      />

       <g>
        <path
          v-for="(d,i) in linkData"
          :key="i"  
          :d="ribbon(d)"
          fill="#d9d9d9"
          :stroke="d.stocks.has(highlightStock)? '#333': '#eee'"
          opacity="0.7"
        />
      </g>
      
      <g v-for="d in arcs"
        :key="d.data.name"  
      >
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
        :d="`M 0, ${-triangleRadius} 
          L${1.732*triangleRadius/2},${triangleRadius/2} 
          L${-1.732*triangleRadius/2},${triangleRadius/2} Z `"
      />
      <path
        fill="#fefefe"
        fill-opacity="1"
        stroke="#777"
        :d="`M 0, ${-triangleRadius} 
          L${1.732*triangleRadius/2},${triangleRadius/2} 
          L${-1.732*triangleRadius/2},${triangleRadius/2} Z `"
        filter="url(#blur)"
      />
      
      <circle cx="0" cy="0" r="10" fill="#efefef" stroke="#aaa"/>
     
      <g :id="stockCode">
        <path
          v-for="d in handledNodes"
          :key="d.name"  
          :d="arcOuter(d)"
          :fill="colorScale[d.type]"
          :stroke="colorScale[d.type]"
          :id="d.name"
          @click="clickOuterNode(stockCode, d.type, d.name)"
        />
      </g>

      <!-- <g>
        <circle 
          v-for="(d,i) in stockPos"
          :key="i"
          r="5"
          :cx="d.radius * Math.cos(d.pos)"
          :cy="d.radius * Math.sin(d.pos)"
          fill="#ccc"
          :stroke="highlightStock == d.name ? '#333': '#ccc'"
          opacity="0.7"
          @click="clickStock(d.name)"
        />
      </g> -->

      <!-- <g ref={chord}></g> -->
      <circle 
        r="5"
        :cx="120 * Math.cos(Math.PI)"
        :cy="-120 * Math.sin(Math.PI)"
        fill="#ccc" 
        opacity="0.7"
      />
    </g>
  </svg>
</template>

<script>
import * as d3 from 'd3';
import DataService from "@/utils/data-service";

const RADIUS_PADDING = 15;
const RADIUS_RANGE = 2.09;

const TYPE_DATA = [
  {name: 'bussiness', value: 1,},
  {name: 'location', value: 1},
  {name: 'people', value: 1}
]

const childrenHash = {
  'bussiness': ['industry', 'concept'],
  'location': ['city', 'province'],
  'people': ['investor', 'management']
}

export default {
  name: 'KnowledgeGraph',
  props: {
    rawData: Object,
    stockCode: String
  },
  data() {
    return {
      width: 550,
      height: 550,
      margin: {
        left: 10,
        top: 10,
        right: 10,
        bottom: 10
      },
      triangleRadius: 80,
      colorScale: {
        'bussiness': '#44930F',
        'industry': '#69BC71',
        'concept': '#69BC9A',

        'people': '#1a589c',
        'investor': '#5C83B6', 
        'management': '#5DA7B9',

        'location': '#81770f',
        'city': '#C8C390', 
        'province': '#A3AE92',
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
      source: {startAngle: 0, endAngle: 0.13277789797532066},
      // 股票的位置数组
      stockPos: [],
      highlightStock: null
    }
  },
  mounted() {
    this.handledData(this.rawData);
  },
  computed: {
    stockScale() {
      return d3.scaleLinear().domain([0,5])
        .range([this.chartWidth/2 - 4.1*RADIUS_PADDING, this.triangleRadius])
    },

    chartWidth() {
      return this.width - this.margin.left - this.margin.right;
    },

    chartHeight() {
      return this.height - this.margin.top - this.margin.bottom;
    },

    arc() {
      return d3.arc()
        .innerRadius(this.chartWidth/2 - 4*RADIUS_PADDING)
        .outerRadius(this.chartWidth /2- 3*RADIUS_PADDING)
        // .innerRadius(this.chartWidth/2 - 2.5*RADIUS_PADDING)
        // .outerRadius(this.chartWidth /2- 0.5*RADIUS_PADDING)
        .padAngle(.02)
    },

    arcOuter() {
      return d3.arc()
        .innerRadius(this.chartWidth/2 - 2.5*RADIUS_PADDING)
        .outerRadius(this.chartWidth /2- RADIUS_PADDING)
        .padAngle(.01)
        .cornerRadius(6);
    },

    arcs() {
      return d3.pie()
        .padAngle(.01)
        .sort(null)
        .value(d => d.value)(TYPE_DATA);
    },

    ribbon() {
      return d3.ribbon()
        .radius(this.chartWidth/2 - 3*RADIUS_PADDING)
        .source(() => this.source)
        .target((d) => d);
    },

  },

  watch: {
    rawData(newValue) {
      this.handledData(newValue);
    }
  },

  methods: {
    clickStock(name) {
      if(this.highlightStock === name) {
        this.highlightStock = null;
      } else {
        this.highlightStock = name;
      }
    },
    clickOuterNode(code, type, name) {
      DataService.post(
        // TODO 还没有对接传过来的stockCode
        "get_knowledge_graph_links",
        [code||'000538', type, name],
        (res) => {
            // {source, target}
          let endNodes = {};
          const resKeys = Object.keys(res);
          const counts = resKeys.map(stock => {
            const propertyOfStock = res[stock];

            // 分类型统计数量
            const countByType = TYPE_DATA.map(({name}) => {
              let count = 0;

              childrenHash[name].forEach(hashKey => {
                if(propertyOfStock[hashKey]) {
                  propertyOfStock[hashKey].forEach(property => {
                    const dictKey = hashKey+'-'+property;
                    if(this.nodeDict[dictKey]) {
                      count++;
                      // endNodes.add(dictKey);
                      if(!endNodes[dictKey]) {
                        endNodes[dictKey] = new Set();
                      }
                      endNodes[dictKey].add(stock)
                    }
                  })
                }
              })

              return count;
            })

            return countByType;
          })

          // 120度的圆弧
          const radiusScale = d3.scaleLinear().domain([0, resKeys.length-1]).range([0, RADIUS_RANGE])

          this.linkData = Object.keys(endNodes).map(d => {
            const {startAngle, endAngle} = this.handledNodes[this.nodeDict[d]]
            return {
              startAngle,
              endAngle,
              stocks: endNodes[d]
            };
          })

          let stockPos = [];
          counts.forEach((count, i)=> {
            count.forEach((countValue, typeIndex) => {
              if(countValue) {
                stockPos.push({
                  name: resKeys[i],
                  pos: radiusScale(i) + typeIndex*RADIUS_RANGE,
                  radius: this.stockScale(countValue)
                })
              }
            })
          })

          // console.log(this.handledNodes);
          console.log(counts)
          console.log(stockPos);

          this.stockPos = stockPos;
          this.source = this.handledNodes[this.nodeDict[type+'-'+name]]
        }
      )
    },
    
    handledData(datum) {
      // console.log(this.arcs)
      let arr = [];
      let dict = {};

      this.arcs.forEach(({data, endAngle, startAngle}) => {
        // console.log(arcData)
        const name = data.name;
        
        let res = 0;
        childrenHash[name].forEach(name => {
          const node = datum[name];
          if(node) {
            const sum = Object.values(node).reduce((a, b) => a+(1/Math.log(b+1)), 0);
            res += sum;
          } 
        })

        const radiusScale = d3.scaleLinear().domain([0, res]).range([0, endAngle - startAngle ]);
        let beginAngle = startAngle;
        childrenHash[name].forEach(name => {
          const node = datum[name];
          node && Object.keys(node).forEach(key => {
              const duration = radiusScale(1/(Math.log(node[key]+1)));
              // console.log(duration)
              dict[name+'-'+key] = arr.length

              arr.push({
                type: name,
                name: key, 
                startAngle: beginAngle,
                endAngle: beginAngle += duration
              })
            }
          );
        })
      })

      this.handledNodes = arr;
      this.nodeDict = dict;
    }
  }
}
</script>

<style scoped>
  circle {
    transition: stroke 300ms ease-in-out;
    cursor: pointer;
  }
</style>