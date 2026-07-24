import axios from "axios";
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL
});
export default api;
export const getDatasets = async (keyword = "") => {

    const response = await api.get(
        "/ai/datasets",
        {
            params:{
                keyword
            }
        }
    );
    return response.data.data.items;
};

export const analyzeDataset = async (datasetId) => {
    const response = await api.post(
        "/ai/analyze",
        {
            dataset_id: datasetId
        }
    );
    
    return response.data.data;
};

export const exportCSV = async (datasetId) => {
    const response = await api.post(
        `/ai/export/${datasetId}`
    );
    return response.data.data;
};