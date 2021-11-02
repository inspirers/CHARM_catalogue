import Vue from "vue";

export default {
  namespaced: true,
  state: () => ({
    tags: [],
    business_areas: [],
    divisions: [],
  }),
  mutations: {
    modifyTag(state, tag) {
      // As division and/or business_area could be modify so we can't use removeTag
      // and it easiest to just filter out all arrays and pushing the new tag
      state.business_areas = state.business_areas.filter((t) => t.id != tag.id);
      state.divisions = state.divisions.filter((t) => t.id != tag.id);
      state.tags = state.tags.filter((t) => t.id != tag.id);

      if (tag.business_area) {
        state.business_areas.push(tag);
      } else if (tag.division) {
        state.divisions.push(tag);
      } else {
        state.tags.push(tag);
      }
    },
    setTags(state, tags) {
      state.tags = tags;
    },
    setBusinessAreas(state, tags) {
      state.business_areas = tags;
    },
    setDivisions(state, tags) {
      state.divisions = tags;
    },
    removeTag(state, tag) {
      // No point wasting cpu time filtering arrays were the tag won't be
      if (tag.business_area) {
        state.business_areas = state.business_areas.filter(
          (t) => t.id != tag.id
        );
      } else if (tag.division) {
        state.divisions = state.divisions.filter((t) => t.id != tag.id);
      } else {
        state.tags = state.tags.filter((t) => t.id != tag.id);
      }
    },
    removeAllTags(state) {
      state.tags = [];
    },
  },
  actions: {
    getTags({ commit }) {
      return new Promise((resolve, reject) => {
        Vue.prototype.$axios
          .get("/tag")
          .then((resp) => {
            commit("removeAllTags");
            const tags = resp.data;
            if (tags.length > 0) {
              commit(
                "setTags",
                tags.filter((t) => !(t.business_area || t.division))
              );
              commit(
                "setBusinessAreas",
                tags.filter((t) => t.business_area)
              );
              commit(
                "setDivisions",
                tags.filter((t) => t.division)
              );
            }
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
    modifyTag({ commit }, tags) {
      return new Promise((resolve, reject) => {
        Vue.prototype.$axios
          .put("/tag", tags)
          .then((resp) => {
            commit("modifyTag", tags);
            resolve(resp);
          })
          .catch((err) => {
            reject(err);
          });
      });
    },
  },
  getters: {
    getTagFromId: (state) => (id) => {
      if (state.tags.length > 0) {
        const result = state.all.filter((t) => t.id == id);
        if (result.length > 0) {
          return result[0];
        }
      }
      return [];
    },
    tags: (state) => {
      return state.tags;
    },
    divisions: (state) => {
      return state.divisions;
    },
    business_areas: (state) => {
      return state.business_areas;
    },
    all: (state) => {
      return state.tags.concat(state.divisions, state.business_areas);
    },
  },
};
