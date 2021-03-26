<template>
  <div>
    <div id="knowledge_graph_title">Knowledge Graph</div>
    <div id="triangle"></div>
  </div>
</template>

<script>

export default {
  name: "KnowledgeGraphView",
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
    }
  },
  mounted: function () {
  },
  methods: {
  },
}
</script>

<style scoped>
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
</style>