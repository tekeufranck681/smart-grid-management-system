import { create } from "zustand";
import { gridNodeService } from "../services/gridNodeService";

export const useGridNodeStore = create((set) => ({
  node: null,
  loading: false,
  error: null,

  createNode: async (gridId, nodeData) => {
    set({ loading: true, error: null });
    try {
      const node = await gridNodeService.createNode(gridId, nodeData);
      set({ node, loading: false });
      return node;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  getNode: async (gridId, nodeId) => {
    set({ loading: true, error: null });
    try {
      const node = await gridNodeService.getNode(gridId, nodeId);
      set({ node, loading: false });
      return node;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  updateNode: async (gridId, nodeId, nodeData) => {
    set({ loading: true, error: null });
    try {
      const node = await gridNodeService.updateNode(gridId, nodeId, nodeData);
      set({ node, loading: false });
      return node;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  updateNodePosition: async (gridId, nodeId, positionData) => {
    set({ loading: true, error: null });
    try {
      const res = await gridNodeService.updateNodePosition(
        gridId,
        nodeId,
        positionData
      );
      set({ loading: false });
      return res;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  deleteNode: async (gridId, nodeId) => {
    set({ loading: true, error: null });
    try {
      const res = await gridNodeService.deleteNode(gridId, nodeId);
      set({ loading: false, node: null });
      return res;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  clearNode: () => set({ node: null, error: null }),
}));
