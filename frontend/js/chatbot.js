/* ==========================================================
   SADA-AI Chatbot
   PART 1
========================================================== */

const API_URL = "http://127.0.0.1:8000/chat";

const chatBox = document.getElementById("chatBox");
const input = document.getElementById("question");
const sendBtn = document.getElementById("sendBtn");


/* ==========================================================
   Event
========================================================== */

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keypress", function(e){

    if(e.key==="Enter"){

        sendMessage();

    }

});


/* ==========================================================
   Kirim Pesan
========================================================== */

async function sendMessage(){

    const question = input.value.trim();

    if(question==="") return;

    addUserMessage(question);

    input.value="";

    showTyping();

    try{

        const response = await fetch(API_URL,{

            method:"POST",

            headers:{

                "Content-Type":"application/json"

            },

            body:JSON.stringify({

                question:question

            })

        });

        const data = await response.json();

        removeTyping();

        addAIMessage(data.answer);

    }

    catch(error){

        removeTyping();

        addAIMessage("❌ Server tidak dapat dihubungi.");

        console.error(error);

    }

}


/* ==========================================================
   Bubble User
========================================================== */

function addUserMessage(message){

    const html = `

    <div class="message user">

        <div class="bubble">

            ${message}

        </div>

    </div>

    `;

    chatBox.insertAdjacentHTML("beforeend",html);

    scrollBottom();

}


/* ==========================================================
   Bubble AI
========================================================== */

function addAIMessage(message){

    const html = `

    <div class="message ai">

        <div class="avatar">

            <i class="fa-solid fa-robot"></i>

        </div>

        <div class="bubble">

            <h4>SADA-AI</h4>

            <p>${message}</p>

        </div>

    </div>

    `;

    chatBox.insertAdjacentHTML("beforeend",html);

    scrollBottom();

}


/* ==========================================================
   Loading
========================================================== */

function showTyping(){

    const html = `

    <div class="message ai" id="typing">

        <div class="avatar">

            <i class="fa-solid fa-robot"></i>

        </div>

        <div class="bubble">

            <h4>SADA-AI</h4>

            <div class="typing">

                <span></span>

                <span></span>

                <span></span>

            </div>

        </div>

    </div>

    `;

    chatBox.insertAdjacentHTML("beforeend",html);

    scrollBottom();

}


function removeTyping(){

    const typing=document.getElementById("typing");

    if(typing){

        typing.remove();

    }

}


/* ==========================================================
   Auto Scroll
========================================================== */

function scrollBottom(){

    setTimeout(()=>{

        chatBox.scrollTop=chatBox.scrollHeight;

    },100);

}


/* ==========================================================
   Welcome
========================================================== */

scrollBottom();

/* ==========================================================
   PART 2
   History, Chips, Copy, Toast, Typing Effect
========================================================== */

let historyData = [];


/* ==========================================================
   Timestamp
========================================================== */

function getCurrentTime(){

    const now = new Date();

    return now.toLocaleTimeString("id-ID",{

        hour:"2-digit",

        minute:"2-digit"

    });

}


/* ==========================================================
   Save History
========================================================== */

function saveHistory(question,answer){

    historyData.unshift({

        question,

        answer,

        time:getCurrentTime()

    });

    renderHistory();

}


/* ==========================================================
   Render History
========================================================== */

function renderHistory(){

    const historyList=document.querySelector(".history-list");

    if(!historyList) return;

    historyList.innerHTML="";

    historyData.forEach(item=>{

        const div=document.createElement("div");

        div.className="history-item";

        div.innerHTML=`

            <h5>${item.question}</h5>

            <small>${item.time}</small>

        `;

        div.onclick=()=>{

            addUserMessage(item.question);

            addAIMessage(item.answer);

        };

        historyList.appendChild(div);

    });

}


/* ==========================================================
   Suggestion Chips
========================================================== */

document.querySelectorAll(".chips button").forEach(btn=>{

    btn.addEventListener("click",()=>{

        input.value=btn.innerText;

        sendMessage();

    });

});


/* ==========================================================
   Toast
========================================================== */

function showToast(message){

    let toast=document.querySelector(".toast");

    if(!toast){

        toast=document.createElement("div");

        toast.className="toast";

        document.body.appendChild(toast);

    }

    toast.innerHTML=message;

    toast.classList.add("show");

    setTimeout(()=>{

        toast.classList.remove("show");

    },2500);

}


/* ==========================================================
   Copy Button
========================================================== */

function copyText(text){

    navigator.clipboard.writeText(text);

    showToast("Jawaban berhasil disalin");

}


/* ==========================================================
   AI Bubble Modern
========================================================== */

function addAIMessage(message){

    const id="copy_"+Date.now();

    const html=`

    <div class="message ai">

        <div class="avatar">

            <i class="fa-solid fa-robot"></i>

        </div>

        <div class="bubble">

            <h4>SADA-AI</h4>

            <p id="${id}"></p>

            <div class="chat-action">

                <button onclick="copyText(document.getElementById('${id}').innerText)">

                    <i class="fa-regular fa-copy"></i>

                    Copy

                </button>

                <button>

                    👍

                </button>

                <button>

                    👎

                </button>

            </div>

        </div>

    </div>

    `;

    chatBox.insertAdjacentHTML("beforeend",html);

    scrollBottom();

    typingEffect(id,message);

}


/* ==========================================================
   Typing Effect
========================================================== */

function typingEffect(id,text){

    const element=document.getElementById(id);

    let i=0;

    const speed=18;

    function typing(){

        if(i<text.length){

            element.innerHTML+=text.charAt(i);

            i++;

            scrollBottom();

            setTimeout(typing,speed);

        }

    }

    typing();

}

/* ==========================================================
   PART 3
========================================================== */


/* ==========================================================
   LOCAL STORAGE
========================================================== */

const STORAGE_KEY="sada_history";

function saveLocal(){

    localStorage.setItem(

        STORAGE_KEY,

        JSON.stringify(historyData)

    );

}

function loadLocal(){

    const data=localStorage.getItem(STORAGE_KEY);

    if(data){

        historyData=JSON.parse(data);

        renderHistory();

    }

}

loadLocal();


/* ==========================================================
   Update Save History
========================================================== */

const oldSaveHistory=saveHistory;

saveHistory=function(question,answer){

    oldSaveHistory(question,answer);

    saveLocal();

}


/* ==========================================================
   SEARCH HISTORY
========================================================== */

const searchBox=document.querySelector(".search-box input");

if(searchBox){

searchBox.addEventListener("keyup",function(){

    const keyword=this.value.toLowerCase();

    document.querySelectorAll(".history-item")

    .forEach(item=>{

        const text=item.innerText.toLowerCase();

        item.style.display=text.includes(keyword)

        ? "block"

        : "none";

    });

});

}


/* ==========================================================
   CLEAR CHAT
========================================================== */

function clearChat(){

    chatBox.innerHTML="";

}

window.clearChat=clearChat;


/* ==========================================================
   EXPORT PDF
========================================================== */

async function exportPDF(){

    const { jsPDF } = window.jspdf;

    const pdf=new jsPDF();

    let text="";

    historyData.forEach(chat=>{

        text+="User : "+chat.question+"\n\n";

        text+="AI : "+chat.answer+"\n\n";

    });

    pdf.text(text,10,10);

    pdf.save("chat-history.pdf");

}

window.exportPDF=exportPDF;


/* ==========================================================
   MARKDOWN
========================================================== */

function renderMarkdown(id,text){

    const element=document.getElementById(id);

    element.innerHTML=marked.parse(text);

}


/* ==========================================================
   CHART DETECTOR
========================================================== */

function containsNumber(text){

    return /\d/.test(text);

}


/* ==========================================================
   Create Chart
========================================================== */

function createChart(containerId){

    const canvas=document.createElement("canvas");

    canvas.height=220;

    document.getElementById(containerId)

    .appendChild(canvas);

    new Chart(canvas,{

        type:"bar",

        data:{

            labels:["A","B","C"],

            datasets:[{

                label:"Nilai",

                data:[12,25,19]

            }]

        }

    });

}


/* ==========================================================
   Loading Bar
========================================================== */

function showProgress(){

    const bar=document.createElement("div");

    bar.id="loadingBar";

    bar.style.height="4px";

    bar.style.background="#C72C41";

    bar.style.width="0%";

    document.body.prepend(bar);

    let width=0;

    const interval=setInterval(()=>{

        width+=10;

        bar.style.width=width+"%";

        if(width>=100){

            clearInterval(interval);

            setTimeout(()=>{

                bar.remove();

            },300);

        }

    },70);

}


/* ==========================================================
   Override Send Message
========================================================== */

const oldSend=sendMessage;

sendMessage=async function(){

    showProgress();

    await oldSend();

}


/* ==========================================================
   DOWNLOAD CHAT
========================================================== */

function downloadText(){

    let text="";

    historyData.forEach(chat=>{

        text+=

        "USER : "+chat.question+

        "\n\nAI : "+chat.answer+

        "\n\n----------------\n\n";

    });

    const blob=new Blob(

        [text],

        {

            type:"text/plain"

        }

    );

    const url=URL.createObjectURL(blob);

    const a=document.createElement("a");

    a.href=url;

    a.download="conversation.txt";

    a.click();

}

window.downloadText=downloadText;


/* ==========================================================
   DARK MODE
========================================================== */

function toggleDark(){

    document.body.classList.toggle("dark");

}

window.toggleDark=toggleDark;