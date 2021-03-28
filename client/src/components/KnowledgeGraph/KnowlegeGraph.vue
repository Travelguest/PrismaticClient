<template>
  <svg :viewbox="`0 0 ${width} ${height}`" :width="width" :height="height">
    <filter id="blur">
      <feGaussianBlur stdDeviation="5"/>
    </filter>
    <g :transform="`translate(${width/2}, ${height/2})`">

      <circle cx="0" cy="0" :r="triangleRadius" fill="none" stroke="#d8d8d8"/>
      <circle cx="0" cy="0" r="120" fill="none" stroke="#d8d8d8"/>
       <g>
        <path
          v-for="d in linkData"
          :key="d.name"  
          :d="ribbon(d)"
          fill="#d9d9d9"
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
        fill="none"
        stroke="#777"
        opacity="0.5"
        :d="`M 0, ${-triangleRadius} 
          L${1.732*triangleRadius/2},${triangleRadius/2} 
          L${-1.732*triangleRadius/2},${triangleRadius/2} Z `"
      />
      <path
        fill="#efefef"
        fill-opacity="0.5"
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

      <!-- <g ref={chord}></g> -->
      
    </g>
  </svg>
</template>

<script>
import * as d3 from 'd3';
const RADIUS_PADDING = 15;
import DataService from "@/utils/data-service";

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
      width: 500,
      height: 500,
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
      linkData: [
       {startAngle: 4.1887902047863905, endAngle: 4.198246826836389},
       {startAngle: 4.3521635245858725, endAngle: 4.435572623446779},
       {startAngle: 1.9394821519108192, endAngle: 2.0943951023931953}
      ],
      handledNodes: [],
      nodeDict: {},
      source: {startAngle: 0, endAngle: 0.13277789797532066}
    }
  },
  mounted() {
    // console.log(this.rawData)
    this.handledData(this.rawData);
  },
  computed: {
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
        .padAngle(.02)
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
    drawChord() {
      const $chord = d3.select(this.$refs.chord);

      const chords = d3.chord()
        .padAngle(.04)
        .sortSubgroups(d3.descending)
        .sortChords(d3.descending)(this.matrix);

      console.log(chords)
      const group = $chord.append("g")
        .selectAll("g")
        .data(chords.groups)
        .enter().append("g");

      group.append("path")
          .attr("class", "group")
          .attr("fill", d => '#efefef')
          // .attr("stroke", d => color(d.index))
          .attr("d", d3.arc()
            .innerRadius(this.chartWidth/2 - 5*RADIUS_PADDING)
            .outerRadius(this.chartWidth /2- 4*RADIUS_PADDING)
          )
    },
    clickOuterNode(code, type, name) {
      DataService.post(
        "get_knowledge_graph_links",
        [code||'000538', type, name],
        (res) => {
          console.log(res)
          let links = [
            // {source, target, stocks}
          ];
          let endNodes = new Set();
          Object.keys(res).forEach(stock => {
            const propertyOfStock = res[stock];
            // 分类型统计数量
            const countByType = TYPE_DATA.map(({name}) => {
              let count = 0;

              childrenHash[name].forEach(hashKey => {
                propertyOfStock[hashKey].forEach(property => {
                  if(this.nodeDict[hashKey+'-'+property]) {
                    count++;
                    endNodes.add(hashKey+'-'+property);
                  }
                })
              })

              return count;
            })
          })

          this.linkData = Array.from(endNodes).map(d => {
            return this.handledNodes[this.nodeDict[d]];
          })
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

      console.log(arr)
      this.handledNodes = arr;
      this.nodeDict = dict;
    }
  }
}
</script>

<style>

</style>