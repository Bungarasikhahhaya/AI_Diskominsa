import { createBrowserRouter } from "react-router-dom";

import Layout from "../components/Layout";
import AnomalyAI from "../pages/AnomalyAI";

const router = createBrowserRouter([
    {
        path: "/",
        element: <Layout />,
        children: [
            {
                index: true,
                element: <AnomalyAI />
            }
        ]
    }
]);

export default router;