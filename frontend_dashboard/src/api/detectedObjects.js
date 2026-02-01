import api from "./api";

export const fetchDetectedObjects = () => {
  return api.get("/detected_objects");
};

export const fetchAlerts = () => {
  return api.get("/alerts");
};
