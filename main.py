from PIL import Image
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from groq import Groq
from typing import List
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--enable-javascript")


img_res: List = []
client = Groq(api_key="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")
def get_chat_response(query):
  completion = client.chat.completions.create(
      model="llama3-8b-8192",
      messages=[
          {
              "role": "user",
              "content": f"You are a genius student \n Based on this {img_res[-1]} \n answer this: {query}"
          }
      ],
      temperature=1,
      max_tokens=1024,
      top_p=1,
      stream=False,
      stop=None,
  )

  # print(completion.choices[0].message)
  return completion.choices[0].message.content
def get_response(img):
  completion = client.chat.completions.create(
      model="llama-3.2-11b-vision-preview",
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "text",
                      "text": "convert all the content in the given image into markdown "
                  },
                  {
                      "type": "image_url",
                      "image_url": {
                          "url": f"{img}"
                      }
                  }
              ]
          }
      ],
      temperature=1,
      max_tokens=1024,
      top_p=1,
      stream=False,
      stop=None,
  )

  # print(completion.choices[0].message)
  img_res.append(completion.choices[0].message.content)
  return completion.choices[0].message.content


class Message(BaseModel):
    message: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class MessageRequest(BaseModel):
    message: str
@app.get("/", response_class=HTMLResponse)
async def homepage():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sleek Model Homepage</title>
        <script src="https://cdn.tailwindcss.com"></script>
            </head>
    <body class="bg-gray-100 flex flex-col justify-center items-center h-screen">
        <div class="w-full max-w-sm bg-white p-8 rounded-lg shadow-lg">
            <h2 class="text-3xl font-semibold text-center text-gray-700 mb-6">Enter Your Data</h2>
            <form id="myForm" onsubmit="handleSubmit(event)">
                <input type="text" name="input_data" placeholder="Type something..."
                       class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4" required>
                <button type="submit"
                        class="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500">Submit</button>
            </form>
            <div id="result" class="mt-6 text-center text-xl text-gray-700"></div>
        </div>

        <!-- PDF Viewer and Chat (Initially hidden) -->
        <div id="pdf-chat-section" class="hidden mt-12 flex w-full">
            <!-- PDF viewer - takes 70% of the screen -->
            <div class="w-2/3">
                <object id="pdf_display" class="w-full h-full" type="application/pdf">
                    PDF cannot be displayed.
                </object>
            </div>
            <!-- Chat/Image section - takes 30% of the screen -->
            <div class="w-1/3 flex flex-col overflow-auto items-center p-4 border-l border-gray-300">
                <img id="destination" class="h-60 w-96 my-2 border border-black" />
                <button id="reload" class="block my-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700" onclick="displayClipboardImage()">Reload</button>
                <div class="overflow-auto h-24 w-fit border-2">
                    <md-span id="display-area">**No data yet**</md-span>
                </div>
                <div id="chat-container" class="w-full h-96 border border-gray-300 flex flex-col justify-end overflow-y-auto bg-gray-100 p-4 rounded"></div>
                <div class="flex w-full mt-2">
                    <input id="chat-input" class="flex-1 p-2 border border-gray-300 rounded mr-2" type="text" placeholder="Type a message...">
                    <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>

<script>
    async function handleSubmit(event) {
        event.preventDefault();  // Prevent the default form submission

        const formData = new FormData(event.target);
        const input_data = formData.get('input_data');

        // Send the data using Fetch API with JSON body
        try {
            const response = await fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: input_data  // Send the input_data as JSON
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const responseData = await response.json();  // Get the JSON response

            // Update the page with the result (using input_data from the response)
            console.log(responseData.message);
            document.getElementById('result').innerHTML = `You entered: ${responseData.message}`;

            // Refresh the PDF object by resetting the data attribute
            const pdfDisplay = document.getElementById('pdf_display');
            pdfDisplay.setAttribute('data', '');  // Clear current data
            setTimeout(() => {
                pdfDisplay.setAttribute('data', responseData.message);  // Set new data
            }, 100);  // Timeout to ensure the element reloads properly

            // Reveal the second part (PDF and chat)
            document.getElementById('pdf-chat-section').classList.remove('hidden');
        } catch (error) {
            // Handle any error that occurred during the fetch
            console.error('Error:', error);
            document.getElementById('result').innerHTML = 'An error occurred. Please try again.';
        }
    }
</script>


        <script>
        const logElement = document.querySelector("#log");
const destinationImage = document.querySelector("#destination");
const inputText = document.querySelector("#input-text");
const responseBox = document.querySelector("#response-box");
const chatContainer = document.getElementById("chat-container");
const chatInput = document.getElementById("chat-input");
            async function submitData(url) {
                try {
                    const response = await fetch(`${window.location.href}send-message`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: `${url}`
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const responseData = await response.json();
                    document.getElementById('display-area').innerText = "Submitted Message: " + responseData.message;
                    console.log('Success:', responseData);
                } catch (error) {
                    console.error('Error:', error);
                }
            }

            function displayClipboardImage() {
                navigator.clipboard.read().then(clipboardItems => {
                    let reader = new FileReader();
                    for (const item of clipboardItems) {
                        const imageTypes = item.types.filter(type => type.startsWith('image/'));
                        if (imageTypes.length > 0) {
                            item.getType(imageTypes[0]).then(blob => {
                                destinationImage.src = URL.createObjectURL(blob);
                                reader.readAsDataURL(blob);
                                reader.onloadend = function () {
                                    let base64String = reader.result;
                                    submitData(base64String);
                                }
                            }).catch(error => {
                                console.log(`Error reading image: ${error.message}`);
                            });
                            break;
                        }
                    }
                }).catch(error => {
                    console.log(`Clipboard access error: ${error.message}`);
                });
            }

            function sendMessage() {
    const message = chatInput.value;
    if (message.trim() === "") return;

    // Display user's message
    const userMessage = document.createElement("div");
    userMessage.className = "chat-message bg-green-200 rounded p-2 self-end max-w-[70%]";
    userMessage.innerText = message;
    chatContainer.appendChild(userMessage);

    chatInput.value = "";

    // Send the user's message to the POST endpoint
    fetch(`${window.location.href}api/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Display the bot's response
        const botMessage = document.createElement("div");
        botMessage.className = "chat-message bg-gray-200 rounded p-2 self-start max-w-[70%]";
        botMessage.innerText = data.response || "No response from server.";
        chatContainer.appendChild(botMessage);
        // chatContainer.scrollTop = chatContainer.scrollHeight;
    })
    .catch(error => {
        console.error("Error:", error);
        const errorMessage = document.createElement("div");
        errorMessage.className = "chat-message bg-red-200 rounded p-2 self-start max-w-[70%]";
        errorMessage.innerText = "An error occurred. Please try again.";
        chatContainer.appendChild(errorMessage);
        // chatContainer.scrollTop = chatContainer.scrollHeight;
    });
}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
content="here"    
# Define the response model
class MessageResponse(BaseModel):
    response: str

# Create a dummy chat endpoint
@app.post("/api/chat", response_model=MessageResponse)
async def chat_endpoint(request: MessageRequest):
    # Extract user message
    user_message = request.message.strip()
    
    # Simulate response generation
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    bot_response = get_chat_response(user_message)

    print(img_res[-1])
    # Return the bot's response
    return {"response": bot_response}

@app.post("/submit")
async def submit_data(request: MessageRequest):
    return JSONResponse(content={"message": request.message})


@app.post("/send-message")
async def send_message(data: Message):
  url=data.message
  print(url)
  try:
    content = get_response(url)
  except:
    content = "sorry no success try again"
  # content = url
  return {"status": "success", "message": content}

