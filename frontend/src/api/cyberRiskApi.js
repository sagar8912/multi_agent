import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const checkHealth = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/health`);
        return response.data;
    } catch (error) {
        console.error("Health check failed:", error);
        throw error;
    }
};

export const analyzeCompany = async (companyData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/analyze-company`, companyData);
        return response.data;
    } catch (error) {
        console.error("Analyze company failed:", error);
        console.error("Backend response:", error.response?.data);
        console.error("Status:", error.response?.status);
        throw error;
    }
};

export const getModifiers = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/modifiers`);
        return response.data;
    } catch (error) {
        console.error("Get modifiers failed:", error);
        throw error;
    }
};

export const getReports = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/reports`);
        return response.data;
    } catch (error) {
        console.error("Get reports failed:", error);
        throw error;
    }
};

export const getReportByFilename = async (filename) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/reports/${filename}`);
        return response.data;
    } catch (error) {
        console.error("Get report failed:", error);
        throw error;
    }
};

export const downloadJsonUrl = (filename) => {
    return `${API_BASE_URL}/reports/${filename}/download-json`;
};

export const downloadPdfUrl = (filename) => {
    return `${API_BASE_URL}/reports/${filename}/download-pdf`;
};
