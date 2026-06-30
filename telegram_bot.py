import os
from telegram import Update
from telegram.ext import Application , CommandHandler , MessageHandler , filters, ContextTypes

TOKEN = "6329684730:AAGrlWSXfHVvoDBJZAf8Otc57hQnS1utCDE"
USERS_FILE = "users.txt"
ADMIN_ID = 6261901431 # Replace 0 with your actual Telegram chat ID to receive order notifications

def load_users():
    loaded_users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(',', 1) # Split only on the first comma
                if len(parts) == 2:
                    try:
                        chat_id = int(parts[0])
                        user_name = parts[1]
                        loaded_users[chat_id] = user_name
                    except ValueError:
                        print(f"Warning: Could not parse line in users.txt: {line.strip()}")
                elif len(parts) == 1: # Handle old format (only chat_id)
                     try:
                        chat_id = int(parts[0])
                        loaded_users[chat_id] = "Unknown User" # Assign a default name
                     except ValueError:
                        print(f"Warning: Could not parse line in users.txt: {line.strip()}")
    return loaded_users

def save_all_users_data():
    with open(USERS_FILE, "w") as file: # Write mode to overwrite
        for chat_id, user_name in users.items():
            file.write(f"{chat_id},{user_name}\n")

users = load_users()

# Cafe menu and user states
CAFE_MENU = {"chai" : 10,
            "coffee" : 20,
            "chai+toast" : 25,
            "gud ki chai" : 30}

# Dictionary to store user-specific cafe interaction state and cart
# Example: user_cafe_state = {chat_id: {'state': 'awaiting_order', 'cart': [], 'total': 0}}
user_cafe_state = {}


#commands
async def start_command(update : Update , context : ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("hello this is a python bot")

async def help_command(update : Update, context : ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("i am here to help you 😇")
    help_desk = {"/cafe" : "to visit our cafe 😇",
                 "/start" : "to check bot is working or not"}
    help_message = "list of commands :\n\n"
    for command, description  in help_desk.items():
        help_message += f"{command} : {description}\n"
    await update.message.reply_text(help_message)
    await update.message.reply_text("type hello to start the chat")
    await update.message.reply_text("@pokemxdr ye mera username bot use kerke esper feedback bhej dena")

# Cafe command
async def cafe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_cafe_state[chat_id] = {'state': 'awaiting_order', 'cart': [], 'total': 0}

    menu_message = "note - dont worry it will not cut you money, just for fun 😉  \n\nWelcome to our cafe! ☕ Here's our menu:\n\n"
    for item, price in CAFE_MENU.items():
        menu_message += f"{item.replace('_', ' ').title():<15} : {price}₹\n"
    menu_message += "\nTo order, just type the item name. Type 'done' when you're finished or 'cancel' to exit."
    await update.message.reply_text(menu_message)


# Broadcast command
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a message to broadcast. Usage: /broadcast <your message>")
        return

    broadcast_message = " ".join(context.args)
    for user_id in users:
        try:
            await context.bot.send_message(user_id,f"Broadcast message: {broadcast_message}")
        except Exception as e:
            print(f"Could not send message to user {user_id}: {e}")
    await update.message.reply_text("Broadcast sent successfully!")

async def reply_to_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /message_user <chat_id> <message>") # Updated usage string
        return

    try:
        target_chat_id = int(context.args[0])
        reply_message = " ".join(context.args[1:])

        await context.bot.send_message(target_chat_id, f"Admin replied: {reply_message}")
        await update.message.reply_text(f"Message sent to user {target_chat_id}.")
    except ValueError:
        await update.message.reply_text("Invalid chat ID. Please provide a numerical chat ID.")
    except Exception as e:
        await update.message.reply_text(f"Failed to send message: {e}")

async def user_data_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not users:
        await update.message.reply_text("No users saved yet.")
        return

    user_list_message = "Saved Users:\n"
    for chat_id, user_name in users.items():
        user_list_message += f"- Name: {user_name}, ID: {chat_id}\n"

    try:
        await context.bot.send_message(ADMIN_ID, user_list_message)
        await update.message.reply_text("User data sent to your admin chat.")
    except Exception as e:
        await update.message.reply_text(f"Failed to send user data: {e}")


#messages
def handel_responces(chat, user_name):
    chat = chat.lower()

    if "hello" in chat:
        return f"hello... {user_name}"
    if "hii" in chat:
        return "hii..."

    return "sorry, i am still learning..\n if you dont know what to do just type 'hello' or '/help"


async def handel_message(update : Update, context : ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_name = update.message.from_user.first_name
    chat_id = update.message.chat_id

    # If new user or name changed, update the users dictionary and save
    if chat_id not in users or users[chat_id] != user_name:
       users[chat_id] = user_name
       save_all_users_data() # Save the updated user data

    print(f"user {user_name} user id texted {text}")

    # Check if the user is in a cafe ordering state
    if chat_id in user_cafe_state and user_cafe_state[chat_id]['state'] == 'awaiting_order':
        if text.lower() == 'done':
            current_cart = user_cafe_state[chat_id]['cart']
            current_total = user_cafe_state[chat_id]['total']
            if not current_cart:
                await update.message.reply_text("Your cart is empty. Do you want to cancel (/cancel) or add more items?")
                return
            cart_summary = "Your order:\n"
            for item in current_cart:
                cart_summary += f"- {item.title()}\n"
            cart_summary += f"Total: {current_total}₹\n"
            cart_summary += "Confirm your order? (yes/no)"
            await update.message.reply_text(cart_summary)
            user_cafe_state[chat_id]['state'] = 'confirming_order'

        elif text.lower() == 'cancel':
            del user_cafe_state[chat_id] # Clear the user's cafe state
            await update.message.reply_text("Cafe order cancelled. Type /cafe to start a new order.")

        elif text.lower() in CAFE_MENU:
            item_name = text.lower()
            item_price = CAFE_MENU[item_name]
            user_cafe_state[chat_id]['cart'].append(item_name)
            user_cafe_state[chat_id]['total'] += item_price
            await update.message.reply_text(f"Added {item_name.title()} to your cart. Current total: {user_cafe_state[chat_id]['total']}₹. Add more or type 'done'.")

        else:
            await update.message.reply_text(f"Sorry, '{text}' nahi hai abhi . Please choose from the menu or type 'done'.")

    elif chat_id in user_cafe_state and user_cafe_state[chat_id]['state'] == 'confirming_order':
        if text.lower() == 'yes':
            final_total = user_cafe_state[chat_id]['total']
            cart_items = user_cafe_state[chat_id]['cart']
            await update.message.reply_text(f"Thank you for your order! Your total bill is {final_total}₹. Enjoy!\nType /cafe to order again.\n\nthank you bhai/bhen bot use kerke esper feedback bhej de")

            # Send order details to admin
            admin_order_message = f"New order received!\nFrom User: {user_name} (ID: {chat_id})\nItems: {', '.join([item.title() for item in cart_items])}\nTotal: {final_total}₹"
            try:
                await context.bot.send_message(ADMIN_ID, admin_order_message)
            except Exception as e:
                print(f"Could not send admin order notification to {ADMIN_ID}: {e}")

            del user_cafe_state[chat_id] # Clear the user's cafe state
        elif text.lower() == 'no':
            await update.message.reply_text("Order not confirmed. Do you want to add/remove something? (add/remove) or 'cancel')")
            user_cafe_state[chat_id]['state'] = 'awaiting_add_remove_action'
        else:
            await update.message.reply_text("Please respond with 'yes' or 'no'.")

    elif chat_id in user_cafe_state and user_cafe_state[chat_id]['state'] == 'awaiting_add_remove_action':
        if text.lower() == 'add':
            await update.message.reply_text("What would you like to add? (Type item name or 'done')")
            user_cafe_state[chat_id]['state'] = 'awaiting_item_to_add'
        elif text.lower() == 'remove':
            if not user_cafe_state[chat_id]['cart']:
                await update.message.reply_text("Your cart is empty, nothing to remove. Type 'add' to add items or 'cancel'.")
                user_cafe_state[chat_id]['state'] = 'awaiting_add_remove_action'
            else:
                cart_items = "Your current items:\n"
                for item in user_cafe_state[chat_id]['cart']:
                    cart_items += f"- {item.title()}\n"
                await update.message.reply_text(f"{cart_items}\nWhat would you like to remove? (Type item name or 'done')")
                user_cafe_state[chat_id]['state'] = 'awaiting_item_to_remove'
        elif text.lower() == 'cancel':
            del user_cafe_state[chat_id]
            await update.message.reply_text("Cafe order cancelled. Type /cafe to start a new order.")
        else:
            await update.message.reply_text("Please type 'add', 'remove', or 'cancel'.")

    elif chat_id in user_cafe_state and user_cafe_state[chat_id]['state'] == 'awaiting_item_to_add':
        if text.lower() == 'done':
            # Go back to confirming order or initial order state
            user_cafe_state[chat_id]['state'] = 'awaiting_order'
            await update.message.reply_text("Finished adding items. Type 'done' again to review your order or 'cancel'.")
        elif text.lower() in CAFE_MENU:
            item_name = text.lower()
            item_price = CAFE_MENU[item_name]
            user_cafe_state[chat_id]['cart'].append(item_name)
            user_cafe_state[chat_id]['total'] += item_price
            await update.message.reply_text(f"Added {item_name.title()}. Current total: {user_cafe_state[chat_id]['total']}₹. Add more or type 'done'.")
        else:
            await update.message.reply_text(f"Sorry, '{text}' is not a valid item. Please choose from the menu or type 'done'.")

    elif chat_id in user_cafe_state and user_cafe_state[chat_id]['state'] == 'awaiting_item_to_remove':
        if text.lower() == 'done':
            # Go back to confirming order or initial order state
            user_cafe_state[chat_id]['state'] = 'awaiting_order'
            await update.message.reply_text("Finished removing items. Type 'done' again to review your order or 'cancel'.")
        elif text.lower() in user_cafe_state[chat_id]['cart']:
            item_name = text.lower()
            item_price = CAFE_MENU[item_name] # Assuming the removed item is from the menu
            user_cafe_state[chat_id]['cart'].remove(item_name)
            user_cafe_state[chat_id]['total'] -= item_price
            await update.message.reply_text(f"Removed {item_name.title()}. Current total: {user_cafe_state[chat_id]['total']}₹. Remove more or type 'done'.")
        else:
            await update.message.reply_text(f"Item '{text}' not found in your cart. Please type an item from your cart or 'done'.")

    else:
        responce = handel_responces(text, user_name)
        await update.message.reply_text(responce)
        print(f"bot reply - '{responce}' to text {text}")
        print(f"{update.message.chat_id}")



#error
async def error(update : Update, context : ContextTypes.DEFAULT_TYPE):
    print(f"Error - Update -  {update} caused error {context.error}")


if __name__ == '__main__':
    print("starting Bot...")
    app = Application.builder().token(TOKEN).build()

    #errors
    app.add_error_handler(error)

    #commands handler
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("cafe", cafe_command)) # Added cafe command handler
    app.add_handler(CommandHandler("message_user", reply_to_user_command)) # Changed command name from reply_to_user
    app.add_handler(CommandHandler("user_data", user_data_command)) # New command handler

    #messages handler
    app.add_handler(MessageHandler(filters.TEXT,handel_message))

    #polling...
    print("polling..")
    # Use run_polling() in Colab after applying nest_asyncio to avoid event loop conflicts
    app.run_polling(close_loop=False)
