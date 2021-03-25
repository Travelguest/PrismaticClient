<template>
  <div id="vue">
    <div id="knowledge_graph_title">Knowledge Graph</div>
    <div id="triangle"></div>
  </div>
</template>

<script>
</script>

<style scoped>
#knowledge_graph_title {
  background-color: #777;
  display: block;
  position: relative;
  padding: 0 20px;
  width: 50%;
  height: 40px;
  line-height: 40px;
  font-size: 26px;
  background: #777;
  color: #fcfcfc;

  display: flex;
  top: 0px;
  font-weight: bold;
  border-radius: 2px;
  box-shadow: 0 1px 2px rgb(26 26 26 / 20%);
}

#triangle {
  position: absolute;
  top: 0px;
  right: 350px;
  border-top: 40px solid #777;
  border-right: 45px solid #ffffff;
  border-bottom: 3px solid #ffff;
}
</style>