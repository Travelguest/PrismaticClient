<template>
  <div id="vue">
    <span :style="{ marginRight: '8px' }">Categories:</span>
    <div v-for="tag in tags" :key="tag">
      <a-checkable-tag
        :checked="selectedTags.indexOf(tag) !== -1"
        @change="(checked) => handleChange(tag, checked)"
      >
        {{ tag }}
      </a-checkable-tag>
    </div>
  </div>
</template>

<script>
import "moment/dist/locale/zh-cn";

export default {
  name: "View",
  data() {
    return {
      tags: ["Movies", "Books", "Music", "Sports"],
      selectedTags: ["Movies", "Books", "Music", "Sports"],
      unselectedTags: [],
    };
  },
  methods: {
    handleChange(tag, checked) {
      //console.log("tag:",tag);
      const { selectedTags } = this;
      const {unselectedTags} = this;
      const nextSelectedTags = checked
        ? [...selectedTags, tag] //如果用户“选中”，就在selectedTag中添加这个新标签；
        : selectedTags.filter((t) => t !== tag); //如果用户取消选择，就在selectedTag中把除了这个标签之外的标签筛选出来


      const nextUnselectedTags = checked
        ? unselectedTags.filter((t) => t !== tag) //如果用户选中，就在selectedTag中把除了这个标签之外的标签筛选出来
        : [...unselectedTags, tag]; //如果用户取消选择，就在selectedTag中添加这个新标签；
      console.log("You are interested in: ", nextSelectedTags);
      console.log("You are not interested in: ", nextUnselectedTags);

      this.selectedTags = nextSelectedTags;
      this.unselectedTags = nextUnselectedTags;
    },
  },
};
</script>
