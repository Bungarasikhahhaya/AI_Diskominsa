import { createBrowserRouter } from "react-router-dom";
import AnomalyAI from "../AnomalyAI";

const router = createBrowserRouter([
    {
        path: "/",
        element: <AnomalyAI />
    }
]);

export default router;