# cogs/document_cog.py

import discord
from discord.ext import commands
import os
import io

from utils.file_processor import extract_text_from_pdf, extract_text_from_epub, extract_text_from_txt
from utils.ai_handler import AIHandler

class DocumentCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_contexts = {}  # {user_id: {"text": "...", "filename": "..."}}
        
        # Load configuration from environment variables
        self.allowed_extensions = ('.pdf', '.epub', '.txt')
        self.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", 1000000))
        self.temp_file_dir = os.getenv("TEMP_FILE_DIR", "temp_uploads")
        
        # Initialize AI Handler
        try:
            self.ai_handler = AIHandler(
                api_key=os.getenv("GOOGLE_API_KEY"),
                model_name=os.getenv("GEMINI_MODEL_NAME")
            )
        except (ValueError, Exception) as e:
            print(f"Failed to initialize AI Handler: {e}")
            self.ai_handler = None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from the bot itself and from guilds (servers)
        if message.author.bot or message.guild:
            return

        # Handle file uploads
        if message.attachments:
            await self.handle_attachment(message)
            return

        # If it's a command, let the command handler process it
        if message.content.startswith(self.bot.command_prefix):
            return
            
        # Handle questions about an existing document
        if message.author.id in self.user_contexts:
            await self.handle_query(message)
        else:
            await message.channel.send(
                f"Hello! I am your document assistant. "
                f"Please upload a file ({', '.join(self.allowed_extensions)}) to start. "
                f"You can type `{self.bot.command_prefix}help` for more commands."
            )

    async def handle_attachment(self, message: discord.Message):
        attachment = message.attachments[0]
        user_id = message.author.id
        
        if not attachment.filename.lower().endswith(self.allowed_extensions):
            await message.channel.send(f"Sorry, I only support {', '.join(self.allowed_extensions)} files.")
            return

        processing_msg = await message.channel.send(f"Received '{attachment.filename}'. Processing... ⏳")
        
        extracted_text = None
        temp_file_path = None
        
        try:
            file_bytes = await attachment.read()
            filename_lower = attachment.filename.lower()

            if filename_lower.endswith('.pdf'):
                extracted_text = extract_text_from_pdf(file_bytes)
            elif filename_lower.endswith('.txt'):
                extracted_text = extract_text_from_txt(file_bytes)
            elif filename_lower.endswith('.epub'):
                # Ebooklib requires a file path, so we save it temporarily
                if not os.path.exists(self.temp_file_dir):
                    os.makedirs(self.temp_file_dir)
                temp_file_path = os.path.join(self.temp_file_dir, f"{user_id}_{attachment.filename}")
                with open(temp_file_path, 'wb') as f:
                    f.write(file_bytes)
                extracted_text = extract_text_from_epub(temp_file_path)

            if extracted_text:
                if len(extracted_text) > self.max_text_length:
                    await message.channel.send(f"⚠️ **Warning:** Document is very long. Context has been truncated to {self.max_text_length:,} characters.")
                
                self.user_contexts[user_id] = {
                    "text": extracted_text[:self.max_text_length], 
                    "filename": attachment.filename
                }
                await processing_msg.edit(content=(
                    f"✅ **Success!** I've processed `{attachment.filename}`.\n"
                    "You can now ask me questions about its content. "
                    f"Type `{self.bot.command_prefix}reset` to upload a new document."
                ))
            else:
                await processing_msg.edit(content=f"❌ **Error:** Could not extract text from `{attachment.filename}`. The file might be empty, corrupted, or password-protected.")

        except Exception as e:
            print(f"Error processing attachment for user {user_id}: {e}")
            await processing_msg.edit(content=f"An unexpected error occurred while processing your file.")
        finally:
            # Clean up the temporary file if it was created
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    async def handle_query(self, message: discord.Message):
        if not self.ai_handler:
            await message.channel.send("The AI service is not configured. Please contact the bot administrator.")
            return
            
        context = self.user_contexts[message.author.id]
        
        async with message.channel.typing():
            response = await self.ai_handler.get_response(
                document_text=context["text"],
                user_query=message.content,
                max_text_length=self.max_text_length
            )
            await message.channel.send(response)

    @commands.command(name="reset", help="Clears the current document context so you can upload a new one.")
    async def reset_context(self, ctx: commands.Context):
        if ctx.author.id in self.user_contexts:
            del self.user_contexts[ctx.author.id]
            await ctx.send("Your document context has been cleared. You can now upload a new file.")
        else:
            await ctx.send("You don't have an active document to reset. Please upload one first.")

    @commands.command(name="status", help="Shows the currently loaded document.")
    async def show_status(self, ctx: commands.Context):
        if ctx.author.id in self.user_contexts:
            context = self.user_contexts[ctx.author.id]
            filename = context['filename']
            text_len = len(context['text'])
            await ctx.send(f"✅ You have a document loaded: `{filename}` ({text_len:,} characters).")
        else:
            await ctx.send("❌ No document is currently loaded.")

# This function is required for the bot to load the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(DocumentCog(bot))