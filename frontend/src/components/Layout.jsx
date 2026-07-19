import { Outlet } from "react-router-dom";
import { useState } from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";

export default function Layout(){

    const [sidebarOpen, setSidebarOpen] = useState(true);

    return(
        <div
            className="
            flex
            bg-zinc-100
            min-h-screen
            overflow-hidden"
        >
            <Sidebar
                open={sidebarOpen}
                setOpen={setSidebarOpen}
            />
            <main
                className="
                flex-1
                p-8
                transition-all
                duration-300
                overflow-x-hidden"
            >
                <Header/>
                <div className="mt-8">
                    <Outlet/>
                </div>
            </main>
        </div>
    );
}