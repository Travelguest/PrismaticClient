<template>
  <div id="vue">
    <div id="knowledge_graph_title">Knowledge Graph</div>
    <div id="triangle"></div>

    <span :style="{ marginRight: '8px' }">Categories:</span>
    <template v-for="tag in tags" :key="tag">
      <a-checkable-tag
        :checked="selectedTags.indexOf(tag) > -1"
        @change="(checked) => handleChange(tag, checked)"
      >
        {{ tag }}
      </a-checkable-tag>
    </template>
  </div>
</template>

<script>
import moment from "moment";
import "moment/dist/locale/zh-cn";

export default {
  name: "View",
  data() {
    return {
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
      periodButtonLoading: false,

      checked1: false,
      checked2: false,
      checked3: false,
      tags: ["Movies", "Books", "Music", "Sports"],
      selectedTags: [],
    };
  },
  methods: {
    handleChange(tag, checked) {
      console.log("tag:",tag);
      const { selectedTags } = this;
      const nextSelectedTags = checked
        ? [...selectedTags, tag]//如果用户“选中”，就在selectedTag中添加这个新标签；
        : selectedTags.filter((t) => t !== tag);//如果用户取消选择，就在selectedTag中把除了这个标签之外的标签筛选出来
      console.log("You are interested in: ", nextSelectedTags);
      this.selectedTags = nextSelectedTags;
    },
  },
};
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
  box-shadow: 0 1px 2px rgba(26 26 26 0.2);
}

#triangle {
  position: absolute;
  top: 0px;
  right: 50%;
  border-top: 40px solid #777;
  border-right: 45px solid #ffffff;
  border-bottom: 3px solid #ffff;
}
</style>