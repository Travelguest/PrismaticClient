<template>
  <div style='height: 100%;width:100%' @click="clickedPinus">
    <a-spin :spinning="loadingTriangle" :delay="100">
      <div :id='`pinus_${id}`' style='height: 100%'>
      </div>
      <div :id="`pinus_${id}_svg`"></div><!--新增-->
    </a-spin>
  </div>
</template>

<script>
import _ from 'lodash';
import * as d3 from 'd3';

export default {
  name: 'PrismView',
  components: {},
  emits: ["clickedPinus"],
  props: {
    id: String,
    loadingTriangle: Boolean,
    correlationTriangle: Object,
  },
  computed: {
    indexName() {
      return !_.isEmpty(this.correlationTriangle)? this.correlationTriangle.name: ''
    },
    matrixColumn() {
      return !_.isEmpty(this.correlationTriangle)? this.correlationTriangle.date: []
    },
    matrixRow() {
      return !_.isEmpty(this.correlationTriangle)? this.correlationTriangle.window: []
    },
    matrixCorr() {
      return !_.isEmpty(this.correlationTriangle)? this.correlationTriangle.corr: []
    },
    squareLength() {
      return (this.height-this.margin.top-this.margin.bottom);
    }
  },
  data () {
    return {
      canvas: null,
      custom: null,
      cellSize: null,
      width: 0,
      height: 0,
      margin: {top: 5, right: 0, bottom: 5, left: 15},
      padding: 0.0,
      svg: null,//新增
      colorScheme: d3.interpolateBrBG,
      // colorScheme: d3.interpolateYlGnBu,
      // colorScheme: d3.interpolateRdYlGn,
      // colorScheme: d3.interpolateYlGn,
      // colorScheme: d3.interpolateYlOrRd,
    }
  },
  watch: {
    correlationTriangle: function() {
      this.bindPinus();

      // this.initTooltip();

      let _this = this;
      let t = d3.timer(function(elapsed) {
        _this.renderPinus();
        if (elapsed > 2000) t.stop();
      });
      this.renderArea();//新增
    }
  },
  mounted() {
    // console.log(this.correlationTriangle);
    this.initPinus();
  },
  methods: {
    clickedPinus(){
      this.$emit('clickedPinus',this.id);
    },
    initPinus() {
      // Initialize canvas
      this.width = this.$el.clientWidth;
      this.height = this.$el.clientHeight;
      // console.log("width height:",this.width,this.height);
      this.canvas = d3.select(`#pinus_${this.id}`)
          .append('canvas')
          .attr('width', this.width)
          .attr('height', this.height);

      this.custom = d3.select(document.createElement('custom'));

      this.svg = d3//新增
        .select(`#pinus_${this.id}_svg`)
        .append("svg")
        .attr("width", this.width + 30)
        .attr("height", this.height + 30)
        // .attr("fill", "red")
        // .attr("transform", `translate(0,${-this.height})`)
        .style("position", "absolute")
        .style("top", 6)
        .style("left", 10)
        .append("g")
        .style("z-index", "1");


      this.bindPinus();
      this.renderArea();//新增

      let _this = this;
      let t = d3.timer(function(elapsed) {
        _this.renderPinus();
        if (elapsed > 2000) t.stop();
      });
    },
    bindPinus() {
      let numRow = this.matrixRow.length,
          cellSize = (this.squareLength / numRow) - this.padding;
      this.cellSize = cellSize;
      this.margin.right = this.width - this.margin.left - this.squareLength;

      let colorScale = d3.scaleSequential()
          .domain([-1,1])
          .interpolator(this.colorScheme);

      let join = this.custom.selectAll('custom.rect').data(this.correlationTriangle.corr);
      let enterSel = join.enter()
          .append('custom')
          .attr('class', 'rect')
          .attr('x', (_, i) => {
            let K = Math.floor((Math.sqrt(8*i+1)-1)/2);
            return this.margin.left + (this.padding + cellSize) * (numRow - 1 - K + i - Math.floor(K*(K+1)/2));
          })
          .attr('y', (_, i) => {
            let K = Math.floor((Math.sqrt(8*i+1)-1)/2);
            return this.margin.top + (this.padding + cellSize) * K;
          })
          .attr('width', 0)
          .attr('height', 0)

      join.merge(enterSel)
          .transition()
          .attr('width', cellSize)
          .attr('height', cellSize)
          .attr('x', (_, i) => {
            let K = Math.floor((Math.sqrt(8*i+1)-1)/2);
            return this.margin.left + (this.padding + cellSize) * (numRow - 1 - K + i - Math.floor(K*(K+1)/2));
          })
          .attr('y', (_, i) => {
            let K = Math.floor((Math.sqrt(8*i+1)-1)/2);
            return this.margin.top + (this.padding + cellSize) * K;
          })
          .attr('fillStyle', (d) => (d === 2)? '#E6E6E6': colorScale(d) );

      join.exit()
          .transition()
          .attr('width', 0)
          .attr('height', 0)
          .remove();
    },


    renderArea() {//新增
      this.date = this.matrixColumn.map((d) => new Date(d));
      this.svg.selectAll("g").remove();

      this.svg
        .append("rect")
        .attr("class", "backGround")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", 4)
        .attr("height", this.height/3)
        .style("fill", "#2D5B81")


      //Title
      this.svg
        .append("g")
        .append("text")
        .attr("class", "textContent")
        .attr("x", 6)
        .attr("y", 12)
        .text("SSEC")
        .style("fill","#2D5B81")
        .style("font-size", "16px");

      //文本4
      this.svg
        .append("g")
        .append("text")
        .attr("class", "textContent")
        .attr("x", 6)
        .attr("y", 25)
        // .attr("x", 40)
        // .attr("y", 29)
        .text("corr")
        .style("fill","#2D5B81")
        .style("font-size", "12px");
        
        if(!this.correlationTriangle) this.svg.selectAll(".backGround").remove();
        if(!this.correlationTriangle) this.svg.selectAll(".textContent").remove();      
    },



    renderPinus() {
      let context = this.canvas.node().getContext('2d');

      context.clearRect(0, 0, this.width, this.height);

      this.custom
          .selectAll('custom.rect')
          .each(function() {
            var node = d3.select(this);
            context.fillStyle = node.attr('fillStyle');
            context.fillRect(node.attr('x'), node.attr('y'), node.attr('width'), node.attr('height'))
          });
    },

  }
}
</script>


<style scoped>
</style>