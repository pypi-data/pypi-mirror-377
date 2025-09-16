# TGZ Messaging SDK

**An Official Python SDK from TechGenzi for sending messages across multiple channels like WhatsApp, Email, and SMS.**

---

## Overview
The **TGZ Messaging SDK** provides a simple and efficient way to integrate messaging functionalities into your Python applications.  
With a focus on **WhatsApp**, this SDK allows you to send both **direct** and **broadcast** messages seamlessly.

---

## Features
- **Multi-channel support**: Easily send messages through various channels, starting with WhatsApp.  
- **Direct messaging**: Send one-to-one messages to your users.  
- **Broadcast messaging**: Send messages to multiple recipients at once.  
- **Easy integration**: A developer-friendly interface for quick and hassle-free setup.  
- **Extensible**: Designed to be easily extendable for future support of additional messaging channels.  

---

## Installation

```bash
pip install tgzmessaging-sdk
```

## How to Use

### Sending a Direct WhatsApp Message

To send a direct message, use `WhatsAppDirect` to define the message content and `WhatsAppClient` to send it.

```python
from tgz_messaging.temp.message_type.direct.whatsapp import WhatsAppDirect
from tgz_messaging.temp.message_client.whatsapp import WhatsAppClient
from tgz_messaging.temp.messaging import Messaging

# Create a direct WhatsApp message
wa_direct = WhatsAppDirect(
    account_sid="ACCOUNT-SID",
    auth_token="AUTH_TOKEN",
    event="Your Event Name",
    recipient="Recipient Number",
    params={
        "header": {
            "param1": "value1"
        },
        "body": {
            "param1": "value1",
            "param2": "value2"
        }
    }
)

# Initialize the client with the message
wa_client = WhatsAppClient(wa_direct)

# Send the message
messaging = Messaging(wa_client)
response = messaging.send_message()

print(response)
```

### Sending a Broadcast WhatsApp Message 

For sending a message to multiple recipients, use WhatsAppBroadcast.

```python
from tgz_messaging.temp.message_type.broadcast import WhatsAppBroadcast
from tgz_messaging.temp.message_client.whatsapp import WhatsAppClient
from tgz_messaging.temp.messaging import Messaging

# Create a broadcast WhatsApp message
wa_broadcast = WhatsAppBroadcast(
    account_sid="ACCOUNT-SID",
    auth_token="AUTH_TOKEN",
    event="Your Event Name",
    recipients=["+919XXXXX", "Recipient 2", "Recipient 3"],
    params={
        "header": {
            "param1": "value1"
        },
        "body": {
            "param1": "value1",
            "param2": "value2"
        }
    }
)

# Initialize the client with the message
wa_client = WhatsAppClient(wa_broadcast)

# Send the message
messaging = Messaging(wa_client)
response = messaging.send_message()

print(response)
```

## Core Modules

### Messaging

The main entry point for sending messages.  
It takes a client instance and calls its `send` method.

- **`Messaging(client: BaseClient)`** → Initializes the messaging service with a specific client.  
- **`send_message()`** → Sends the message using the provided client.

---

### WhatsAppClient

The client responsible for handling WhatsApp messages.

- **`WhatsAppClient(message_type: MessageType)`** → Initializes the client with a message type, either `WhatsAppDirect` or `WhatsAppBroadcast`.

---

### WhatsAppDirect

Used to create direct messages for WhatsApp.

```code
WhatsAppDirect(
    account_sid: str,
    auth_token: str,
    event: str,
    recipient: str,
    params: dict
)
```

- project → Your project's identifier.
- event → The type of event triggering the message.
- recipient → The phone number of the recipient.
- params → A dictionary containing message parameters (header, body, etc.).


### WhatsAppBroadcast

Used to create broadcast messages.

```code
WhatsAppBroadcast(
    account_sid: str,
    auth_token: str,
    event: str,
    recipients: list,
    params: dict
)
```

- project → Your project's identifier.
- event → The type of event for the broadcast.
- recipients → A list of recipient phone numbers.
- params → A dictionary with message parameters (header, body, etc.).


## Project Structure

The SDK is organized into the following key modules:

```code
tgz_messaging/
├── message_type/      # Contains classes for different message types (direct, broadcast)
│   ├── direct/
│   └── broadcast/
├── message_client/    # Includes clients for various messaging products like WhatsApp
└── messaging/         # Main module that orchestrates the message sending process
```
