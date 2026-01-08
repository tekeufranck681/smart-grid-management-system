import { create } from "zustand";
import { scenarioService } from "../services/scenarioService";

export const useScenarioStore = create((set) => ({
  scenario: null,
  scenarios: [],
  loading: false,
  error: null,

  createScenario: async (gridId, scenarioData) => {
    set({ loading: true, error: null });
    try {
      const scenario = await scenarioService.createScenario(gridId, scenarioData);
      set({ scenario, loading: false });
      return scenario;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  addScenarioEvent: async (scenarioId, eventData) => {
    set({ loading: true, error: null });
    try {
      const event = await scenarioService.addScenarioEvent(scenarioId, eventData);
      set((state) => ({
        scenario: {
          ...state.scenario,
          events: [...(state.scenario?.events || []), event],
        },
        loading: false,
      }));
      return event;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  listScenariosByGrid: async (gridId) => {
    set({ loading: true, error: null });
    try {
      const result = await scenarioService.listScenariosByGrid(gridId);
      set({ scenarios: result.scenarios, loading: false });
      return result.scenarios;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  getScenario: async (scenarioId) => {
    set({ loading: true, error: null });
    try {
      const scenario = await scenarioService.getScenario(scenarioId);
      set({ scenario, loading: false });
      return scenario;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  updateScenarioStatus: async (scenarioId, newStatus) => {
    set({ loading: true, error: null });
    try {
      const scenario = await scenarioService.updateScenarioStatus(scenarioId, newStatus);
      set({ scenario, loading: false });
      return scenario;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  deleteScenario: async (scenarioId) => {
    set({ loading: true, error: null });
    try {
      const result = await scenarioService.deleteScenario(scenarioId);
      set({ scenario: null, loading: false });
      return result;
    } catch (error) {
      set({ loading: false, error: error.message });
      throw error;
    }
  },

  clearScenario: () => set({ scenario: null, error: null }),
}));
