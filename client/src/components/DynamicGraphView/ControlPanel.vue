<template>
  <div class="text-color" style="height: 100%">
    <div class="panel-header">PRISMATIC</div>
    <div class="panel-header-end"></div>
    <div>
      <a-row>
        <a-col
          :span="12"
          style="line-height: 40px; font-size: 16px; font-weight: bold"
        >
          <text style="color:#263238">Select stocks and correlation</text>
        </a-col>
        <a-col :span="9">
          <a-slider
            range
            :tooltipVisible="false"
            v-model:value="correlationRange"
            :min="-1"
            :max="1"
            :step="0.01"
            :marks="correlationMarks"
            @change="onCorrelationSliderChange"
          />
        </a-col>
        <a-col :span="3" align="middle" style="padding: 2px">
          <a-button
            shape="circle"
            style="background: #ECEFF1; color: #546E7A"
            :loading="correlationButtonLoading"
            :disabled="stockButtonDisabled"
            @click="onCorrelationButtonClick"
          >
            <template #icon><FilterOutlined /></template>
          </a-button>
        </a-col>
      </a-row>
      <a-row type="flex" class="panel">
        <a-select
          style="
            width: 100%;
            border: 1px solid #aeaeae;
            box-shadow: 0 10px 10px -6px rgba(21, 85, 194, 0.13);
            border-radius: 5px;
          "
          :maxTagCount="5"
          v-model:value="stockSelected"
          mode="multiple"
          allowClear
          placeholder="Search by stocks"
          option-label-prop="label"
        >
          <a-select-option
            disabled
            style="
              color: steelblue;
              font-size: 12px;
              line-height: 50px;
              height: 50px;
            "
          >
            <p style="text-align: center; width: 20%; display: inline-block">
              <b>Code</b>
            </p>
            <p style="text-align: center; width: 25%; display: inline-block">
              <b>Company</b>
            </p>
            <p style="text-align: center; width: 25%; display: inline-block">
              <b>Sector</b>
            </p>
            <p style="text-align: center; width: 30%; display: inline-block">
              <b>Subsector</b>
            </p>
          </a-select-option>
          <a-select-option
            v-for="stock in stockList"
            :key="stock.ts_code"
            :value="stock.ts_code"
            style="font-size: 12px"
          >
            <p
              style="
                text-align: center;
                width: 20%;
                display: inline-block;
                line-height: 15px;
                height: 15px;
              "
            >
              {{ stock.ts_code }}
            </p>
            <p
              style="
                text-align: center;
                width: 25%;
                display: inline-block;
                line-height: 15px;
                height: 15px;
              "
            >
              {{ stock.name }}
            </p>
            <p
              style="
                text-align: center;
                width: 25%;
                display: inline-block;
                line-height: 15px;
                height: 15px;
              "
            >
              {{ stock.level1 }}
            </p>
            <p
              style="
                text-align: center;
                width: 30%;
                display: inline-block;
                line-height: 15px;
                height: 15px;
              "
            >
              {{ stock.level3 }}
            </p>
          </a-select-option>
        </a-select>
      </a-row>
    </div>

    <a-divider
      style="font-size: 16px; font-weight: bold; padding-top: 10px; margin: 0; color: #263238"
      >Correlated clusters</a-divider
    >
    <dynamic-graph-view
      class="dynamic-graph"
      :corr-distribution="corrDistribution"
      :corr-cluster="corrCluster"
      :corr-cluster-update="corrClusterUpdate"
      :selected-stock="selectedStock"
      :threshold-range="correlationRange"
      @clicked-year="onYearClick"
      @update-year-brush="handleUpdateYearBrush"
    >
    </dynamic-graph-view>

    <a-divider
      style="
        font-size: 16px;
        font-weight: bold;
        padding-top: 10px;
        padding-bottom: 2px;
        margin: 0;
        color: #263238;
      "
      >Business tag filters</a-divider
    >
    <a-row justify="space-around" class="tag-cards">
      <a-tabs tabPosition="top" size="small">
        <a-tab-pane key="L1" tab="Industry" force-render class="tagOfIndustry">
          <a-checkable-tag
            v-for="tag in businessTag.L1"
            :key="tag"
            style="margin: 5px"
            :checked="selectedTagsIndustry.indexOf(tag) !== -1"
            @change="(checked) => handleChangeIndustry(tag, checked)"
          >
            <!--color: #884ed8;
              background-color: #faf2ff;
              border: #dbbcf8 1px solid;-->
            {{ tag.name }}({{ tag.count }})
          </a-checkable-tag>
        </a-tab-pane>
        <a-tab-pane key="L2" tab="Sector" class="tagOfSector">
          <a-checkable-tag
            v-for="tag in businessTag.L2"
            :key="tag"
            style="margin: 5px"
            :checked="selectedTagsSector.indexOf(tag) !== -1"
            @change="(checked) => handleChangeSector(tag, checked)"
          >
            <!--color: #50abff;
              background-color: #eaf8ff;
              border: #a2dbff 1px solid;-->
            {{ tag.name }}({{ tag.count }})
          </a-checkable-tag>
        </a-tab-pane>
        <a-tab-pane key="L3" tab="Subsector" class="tagOfSubsector">
          <a-checkable-tag
            v-for="tag in businessTag.L3"
            :key="tag"
            style="margin: 5px"
            :checked="selectedTagsSubsector.indexOf(tag) !== -1"
            @change="(checked) => handleChangeSubsector(tag, checked)"
          >
            <!--color: #51d3d2;
              background-color: #eafffc;
              border: #99ece3 1px solid;  -->
            {{ tag.name }}({{ tag.count }})
          </a-checkable-tag>
        </a-tab-pane>
        <a-tab-pane key="Concept" tab="Concept" class="tagOfConcept">
          <a-checkable-tag
            v-for="tag in businessTag.concept"
            :key="tag"
            style="margin: 5px"
            :checked="selectedTagsConcept.indexOf(tag) !== -1"
            @change="(checked) => handleChangeConcept(tag, checked)"
          >
            <!--color: #fba343;
              background-color: #fff8ea;
              border: #ffdba2 1px solid;-->
            {{ tag.name }}({{ tag.count }})
          </a-checkable-tag>
        </a-tab-pane>
        <!--        <template #tabBarExtraContent>-->
        <!--          <a-button>Filter</a-button>-->
        <!--        </template>-->
      </a-tabs>
    </a-row>
  </div>
</template>

<script>
import DataService from "@/utils/data-service";
import index_corr_dist from "@/components/data/index_corr_dist.json";
import corr_clusters_all_years from "@/components/data/corr_clusters_all_years.json";
import business_tag_table from "@/components/data/business_tag_table.json";
import DynamicGraphView from "@/components/DynamicGraphView/DynamicGraphView";
import { FilterOutlined } from "@ant-design/icons-vue";
import _ from "lodash";
export default {
  name: "ControlPanel",
  components: {
    DynamicGraphView,
    FilterOutlined,
  },
  props: {},
  emits: ["get-correlation-matrix"],
  data() {
    return {
      stockList: [
        {
          ts_code: "000001.SH",
          name: "上证指数",
          level1: "index",
          level3: "composite",
        },
      ],
      stockSelectionNumMax: 10,
      stockSelected: ["000652", "000538"],

      corrDistribution: index_corr_dist,

      correlationRange: [0.7, 1],
      correlationMarks: {
        0.7: { style: { top: "-30px", "font-size": "12px" }, label: "0.7" },
        0: { style: { top: "-30px", "font-size": "12px" }, label: "0" },
        1: { style: { top: "-30px", "font-size": "12px" }, label: "1" },
      },
      correlationButtonLoading: false,

      corrCluster: corr_clusters_all_years,
      corrClusterUpdate: 1, //告诉子组件corrCluster更新的
      businessTag: business_tag_table,

      //tagsIndustry: business_tag_table.L1,
      selectedTagsIndustry: business_tag_table.L1,
      unselectedTagsIndustry: [],

      selectedTagsSector: business_tag_table.L2,
      unselectedTagsSector: [],

      selectedTagsSubsector: business_tag_table.L3,
      unselectedTagsSubsector: [],

      selectedTagsConcept: business_tag_table.concept,
      unselectedTagsConcept: [],
      selectedStock: ["000652", "000538"],
    };
  },
  computed: {
    stockButtonDisabled() {
      return !this.stockSelected.length;
    },
    // selectedTagsIndustry() {
    //   return this.businessTag.L1;
    // },
    // selectedTagsSector() {
    //   return this.businessTag.L2;
    // },
    // selectedTagsSubsector() {
    //   return this.businessTag.L3;
    // },
    // selectedTagsConcept() {
    //   return this.businessTag.concept;
    // },
  },
  watch: {
    stockSelected: function (newVal) {
      // Remove the last element if the selected number of stocks exceeds maximum
      if (newVal.length >= this.stockSelectionNumMax) {
        this.stockSelected.splice(this.stockSelectionNumMax, 1);
      } else {
        // Whenever stocks are selected, update the correlation distribution
        DataService.post("get_corr_dist", this.stockSelected, (data) => {
          this.selectedStock = _.cloneDeep(this.stockSelected);
          this.corrDistribution = data;
        });
      }
    },
  },
  mounted: function () {
    DataService.get("get_stock_list", (data) => {
      this.stockList = data;
    });
  },
  methods: {
    handleUpdateYearBrush: function (left, right, year) {
      // this.correlationRange[0] = left;
      // this.correlationRange[1] = right;
      console.log([year, left, right]);
      DataService.post(
        "get_corr_clusters_one_year",
        [year, left, right],
        (data) => {
          this.corrCluster[year] = data;
          this.corrClusterUpdate = this.corrClusterUpdate + 1;
          //  console.log(`corrCluster${year}更新了data:`,this.corrClusterUpdate,data);
          // this.corrCluster = data;
          // this.correlationButtonLoading = !this.correlationButtonLoading;
        }
      );
    },
    onCorrelationSliderChange(val) {
      this.correlationMarks = {
        0: { style: { top: "-32px", "font-size": "12px" }, label: "0" },
      };
      this.correlationMarks[val[0]] = {
        style: { top: "-32px", "font-size": "12px" },
        label: "" + val[0],
      };
      this.correlationMarks[val[1]] = {
        style: { top: "-32px", "font-size": "12px" },
        label: "" + val[1],
      };
    },
    onCorrelationButtonClick() {
      this.correlationButtonLoading = !this.correlationButtonLoading;
      DataService.post(
        "get_corr_clusters_all_years",
        this.correlationRange,
        (data) => {
          this.corrCluster = data;
          this.correlationButtonLoading = !this.correlationButtonLoading;
        }
      );
      DataService.post(
        "get_business_tag_table",
        this.correlationRange,
        (data) => {
          this.businessTag = data;
          this.selectedTagsIndustry = this.businessTag.L1;

          this.selectedTagsSector = this.businessTag.L2;

          this.selectedTagsSubsector = this.businessTag.L3;

          this.selectedTagsConcept = this.businessTag.concept;
          this.unselectedTagsIndustry = [];

          this.unselectedTagsSector = [];

          this.unselectedTagsSubsector = [];

          this.unselectedTagsConcept = [];
        }
      );
    },
    onYearClick(topNodes, year) {
      // console.log("传过来了：", topNodes, year);
      // TODO: put a button to select filter
      // eslint-disable-next-line no-constant-condition
      // let nodes = true ? topNodes : this.corrCluster[year].nodes;
      this.$emit("get-correlation-matrix", topNodes, year);
    },

    handleChangeIndustry(tag, checked) {
      //console.log("this.color"+this.);
      // console.log("tag:",tag,checked);
      const { selectedTagsIndustry } = this;
      const { unselectedTagsIndustry } = this;
      // console.log("selectedTagsIndustry:",selectedTagsIndustry,unselectedTagsIndustry);
      const nextSelectedTagsIndustry = checked
        ? [...selectedTagsIndustry, tag] //如果用户“选中”，就在selectedTag中添加这个新标签；
        : selectedTagsIndustry.filter((t) => t !== tag); //如果用户取消选择，就在selectedTag中把除了这个标签之外的标签筛选出来

      const nextUnselectedTagsIndustry = checked
        ? unselectedTagsIndustry.filter((t) => t !== tag) //如果用户选中，就在selectedTag中把除了这个标签之外的标签筛选出来
        : [...unselectedTagsIndustry, tag]; //如果用户取消选择，就在selectedTag中添加这个新标签；
      console.log("You are interested in: ", nextSelectedTagsIndustry);
      console.log("You are not interested in: ", nextUnselectedTagsIndustry);

      this.selectedTagsIndustry = nextSelectedTagsIndustry;
      this.unselectedTagsIndustry = nextUnselectedTagsIndustry;
    },

    handleChangeSector(tag, checked) {
      const { selectedTagsSector } = this;
      const { unselectedTagsSector } = this;
      const nextSelectedTagsSector = checked
        ? [...selectedTagsSector, tag] //如果用户“选中”，就在selectedTag中添加这个新标签；
        : selectedTagsSector.filter((t) => t !== tag); //如果用户取消选择，就在selectedTag中把除了这个标签之外的标签筛选出来

      const nextUnselectedTagsSector = checked
        ? unselectedTagsSector.filter((t) => t !== tag) //如果用户选中，就在selectedTag中把除了这个标签之外的标签筛选出来
        : [...unselectedTagsSector, tag]; //如果用户取消选择，就在selectedTag中添加这个新标签；
      console.log("You are interested in: ", nextSelectedTagsSector);
      console.log("You are not interested in: ", nextUnselectedTagsSector);

      this.selectedTagsSector = nextSelectedTagsSector;
      this.unselectedTagsSector = nextUnselectedTagsSector;
    },

    handleChangeSubsector(tag, checked) {
      const { selectedTagsSubsector } = this;
      const { unselectedTagsSubsector } = this;
      const nextSelectedTagsSubsector = checked
        ? [...selectedTagsSubsector, tag] //如果用户“选中”，就在selectedTag中添加这个新标签；
        : selectedTagsSubsector.filter((t) => t !== tag); //如果用户取消选择，就在selectedTag中把除了这个标签之外的标签筛选出来

      const nextUnselectedTagsSubsector = checked
        ? unselectedTagsSubsector.filter((t) => t !== tag) //如果用户选中，就在selectedTag中把除了这个标签之外的标签筛选出来
        : [...unselectedTagsSubsector, tag]; //如果用户取消选择，就在selectedTag中添加这个新标签；
      console.log("You are interested in: ", nextSelectedTagsSubsector);
      console.log("You are not interested in: ", nextUnselectedTagsSubsector);

      this.selectedTagsSubsector = nextSelectedTagsSubsector;
      this.unselectedTagsSubsector = nextUnselectedTagsSubsector;
    },

    handleChangeConcept(tag, checked) {
      const { selectedTagsConcept } = this;
      const { unselectedTagsConcept } = this;
      const nextSelectedTagsConcept = checked
        ? [...selectedTagsConcept, tag] //如果用户“选中”，就在selectedTag中添加这个新标签；
        : selectedTagsConcept.filter((t) => t !== tag); //如果用户取消选择，就在selectedTag中把除了这个标签之外的标签筛选出来

      const nextUnselectedTagsConcept = checked
        ? unselectedTagsConcept.filter((t) => t !== tag) //如果用户选中，就在selectedTag中把除了这个标签之外的标签筛选出来
        : [...unselectedTagsConcept, tag]; //如果用户取消选择，就在selectedTag中添加这个新标签；
      console.log("You are interested in: ", nextSelectedTagsConcept);
      console.log("You are not interested in: ", nextUnselectedTagsConcept);

      this.selectedTagsConcept = nextSelectedTagsConcept;
      this.unselectedTagsConcept = nextUnselectedTagsConcept;
    },
  },
};
</script>

<style scoped>

.panel-header {
  position: relative;
  padding: 0 20px;
  width: 309.531px;
  height: 40px;
  line-height: 40px;
  font-size: 24px;
  background: #455A64;
  color: #fcfcfc;
  display: flex;
  font-weight: bold;
  border-radius: 2px;
  box-shadow: 0 1px 2px rgba(26 26 26 0.2);
}

.panel-header-end {
  position: absolute;
  top: 2px;
  left: 309.531px;
  border-top: 40px solid #455A64;
  border-right: 45px solid #ffffff;
  border-bottom: 3px solid #ffffff;
}

.panel {
  margin-top: -15px;
  padding: 4px;
}
.dynamic-graph {
  height: 710px;
  overflow: auto;
}
.tag-cards {
  height: 210px;
  overflow: auto;
}

/* 滚动槽 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.06);
  -webkit-box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.08);
}
/* 滚动条滑块 */
::-webkit-scrollbar-thumb {
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.12);
  -webkit-box-shadow: inset 0 0 10px rgba(53, 31, 31, 0.2);
}
::v-deep .ant-tag-checkable {
  background-color: #f2f4f5;
  border-color: #f0f0f1;
  cursor: pointer;
  margin: 5px;
  color: #565657;
}

::v-deep .tagOfIndustry .ant-tag-checkable-checked {
  color: #7D5BB2;
  background-color: #EFEAF5;
  border: #AE98CF 1px solid;
}

::v-deep .tagOfSector .ant-tag-checkable-checked {
  color: #7D5BB2;
  background-color: #EFEAF5;
  border: #AE98CF 1px solid;
}

::v-deep .tagOfSubsector .ant-tag-checkable-checked {
  color: #7D5BB2;
  background-color: #EFEAF5;
  border: #AE98CF 1px solid;
}

::v-deep .tagOfConcept .ant-tag-checkable-checked {
  color: #7D5BB2;
  background-color: #EFEAF5;
  border: #AE98CF 1px solid;
}
</style>
