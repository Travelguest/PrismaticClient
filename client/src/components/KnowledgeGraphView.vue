<template>
  <div class="knowledge-container">
    <div id="knowledge_graph_title"><div id="knowledge_graph_text">Knowledge Graph</div></div>
    <div id="triangle"></div>
    <div class="svg-wrapper">
      <KnowledgeGraph :rawData="nodes" :stock-code="stockCode" />
    </div>
  </div>
</template>

<script>
import data from './data/knowledge_count.json';
import KnowledgeGraph from './KnowledgeGraph/KnowlegeGraph';

export default {
  name: "KnowledgeGraphView",
  components:{
    KnowledgeGraph
  },
  props: {
    stockCode: String,
    knowledgeGraphCount: Object,
  },
  watch: {
    knowledgeGraphCount: function () {
      // console.log(this.knowledgeGraphCount)
    },
  },
  data() {
    return {
      nodes: data,
    }
  },
  mounted: function () {
  },
  methods: {},
};
</script>

<style scoped>

.knowledge-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

#knowledge_graph_title {
  position: absolute;
  right: 0;
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

#knowledge_graph_text {
  position: absolute;
  right: 0;
  padding-right: 20px;
  text-align: right;
}

#triangle {
  position: absolute;
  top: 0;
  right: 309.531px;
  border-top: 40px solid #777;
  border-left: 45px solid #ffffff;
  border-bottom: 3px solid #ffff;
}

.svg-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
}
</style>