require('dotenv').config();
const { Client, GatewayIntentBits, AttachmentBuilder, EmbedBuilder } = require('discord.js');
const { createCanvas, loadImage } = require('@napi-rs/canvas');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

client.once('ready', () => {
  console.log(`✅ Bot online as ${client.user.tag}`);
});

// Helper function to create the player data image
async function createPlayerCard(username, avatarUrl, score, level) {
  // 1. Create a blank canvas (700px width x 250px height)
  const canvas = createCanvas(700, 250);
  const ctx = canvas.getContext('2d');

  // 2. Draw Background Card
  ctx.fillStyle = '#1e1f22'; // Dark gray card
  ctx.roundRect(0, 0, canvas.width, canvas.height, 20);
  ctx.fill();

  // Accent Top Bar
  ctx.fillStyle = '#5865F2'; // Discord Blurple
  ctx.fillRect(0, 0, canvas.width, 15);

  // 3. Draw Player Avatar (Circular)
  try {
    const avatar = await loadImage(avatarUrl);
    ctx.save();
    ctx.beginPath();
    ctx.arc(100, 130, 60, 0, Math.PI * 2, true);
    ctx.closePath();
    ctx.clip();
    ctx.drawImage(avatar, 40, 70, 120, 120);
    ctx.restore();
  } catch (err) {
    console.error("Could not load avatar image:", err);
  }

  // 4. Draw Player Statistics Text
  ctx.fillStyle = '#FFFFFF';
  ctx.font = 'bold 32px sans-serif';
  ctx.fillText(username, 180, 100);

  ctx.fillStyle = '#B5BAC1';
  ctx.font = '22px sans-serif';
  ctx.fillText(`Level: ${level}`, 180, 145);
  ctx.fillText(`Score: ${score} PTS`, 180, 180);

  // 5. Turn Canvas into Buffer
  return canvas.toBuffer('image/png');
}

// Command: Trigger image creation using !profile or !stats
client.on('messageCreate', async (message) => {
  if (message.author.bot) return;

  if (message.content === '!profile' || message.content === '!stats') {
    // Example player data (replace with actual API data if fetching from a database)
    const playerData = {
      name: message.author.username,
      avatar: message.author.displayAvatarURL({ extension: 'png' }),
      score: 1250,
      level: 12,
    };

    // Generate image buffer
    const imageBuffer = await createPlayerCard(
      playerData.name,
      playerData.avatar,
      playerData.score,
      playerData.level
    );

    // Create attachment for Discord
    const attachment = new AttachmentBuilder(imageBuffer, { name: 'player-card.png' });

    // Send inside an embed
    const embed = new EmbedBuilder()
      .setTitle(`🎮 Player Profile: ${playerData.name}`)
      .setColor(0x5865F2)
      .setImage('attachment://player-card.png') // Refers to the attached file name
      .setTimestamp();

    await message.channel.send({ embeds: [embed], files: [attachment] });
  }
});

client.login(process.env.DISCORD_TOKEN);
