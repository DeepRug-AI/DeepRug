const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class SocialMediaService {
    constructor(config) {
        this.config = config;
        this.platforms = {
            twitter: this.postToTwitter.bind(this),
            telegram: this.postToTelegram.bind(this),
            discord: this.postToDiscord.bind(this),
            reddit: this.postToReddit.bind(this),
            weibo: this.postToWeibo.bind(this)
        };
    }

    async postContent(content, platforms = ['twitter', 'telegram', 'discord', 'reddit', 'weibo']) {
        const results = [];
        for (const platform of platforms) {
            if (this.platforms[platform]) {
                try {
                    const result = await this.platforms[platform](content);
                    results.push({ platform, success: true, result });
                } catch (error) {
                    console.error(`Error posting to ${platform}:`, error);
                    results.push({ platform, success: false, error: error.message });
                }
            }
        }
        return results;
    }

    async postToTwitter(content) {
        const { text, mediaPath, replyToId } = content;
        const data = new FormData();
        data.append('text', text);

        if (mediaPath && fs.existsSync(mediaPath)) {
            data.append('media', fs.createReadStream(mediaPath));
        }

        if (replyToId) {
            data.append('reply', { in_reply_to_tweet_id: replyToId });
        }

        const response = await axios.post(
            'https://api.twitter.com/2/tweets',
            data,
            {
                headers: {
                    ...data.getHeaders(),
                    'Authorization': `Bearer ${this.config.twitter.accessToken}`
                }
            }
        );

        return response.data;
    }

    async postToTelegram(content) {
        const { text, mediaPath, replyToMessageId } = content;
        const method = mediaPath ? 'sendPhoto' : 'sendMessage';
        const data = mediaPath ? 
            { photo: fs.createReadStream(mediaPath), caption: text } :
            { text };

        if (replyToMessageId) {
            data.reply_to_message_id = replyToMessageId;
        }

        const response = await axios.post(
            `https://api.telegram.org/bot${this.config.telegram.botToken}/${method}`,
            {
                chat_id: this.config.telegram.channelId,
                ...data
            },
            {
                headers: { 'Content-Type': 'application/json' }
            }
        );

        return response.data;
    }

    async postToDiscord(content) {
        const { text, mediaPath, threadId } = content;
        const data = { content: text };

        if (threadId) {
            data.thread_id = threadId;
        }

        if (mediaPath) {
            const form = new FormData();
            form.append('file', fs.createReadStream(mediaPath));
            form.append('payload_json', JSON.stringify(data));

            return await axios.post(
                this.config.discord.webhookUrl,
                form,
                { headers: form.getHeaders() }
            );
        }

        return await axios.post(
            this.config.discord.webhookUrl,
            data,
            { headers: { 'Content-Type': 'application/json' } }
        );
    }

    async postToReddit(content) {
        const { text, mediaPath, subreddit } = content;
        const data = {
            title: text.split('\n')[0],
            text: text,
            sr: subreddit || this.config.reddit.defaultSubreddit
        };

        if (mediaPath) {
            data.image = fs.createReadStream(mediaPath);
        }

        const response = await axios.post(
            'https://oauth.reddit.com/api/submit',
            data,
            {
                headers: {
                    'Authorization': `Bearer ${this.config.reddit.accessToken}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        return response.data;
    }

    async postToWeibo(content) {
        const { text, mediaPath } = content;
        const data = new FormData();
        data.append('status', text);

        if (mediaPath && fs.existsSync(mediaPath)) {
            data.append('pic', fs.createReadStream(mediaPath));
        }

        const response = await axios.post(
            'https://api.weibo.com/2/statuses/share.json',
            data,
            {
                headers: {
                    ...data.getHeaders(),
                    'Authorization': `OAuth2 ${this.config.weibo.accessToken}`
                }
            }
        );

        return response.data;
    }

    async distributeTradeContent(tradeData, memeImage, confessionVoice) {
        const content = {
            text: `🚨 Trade Alert! ${tradeData.symbol}\n` +
                  `💰 Price: ${tradeData.price}\n` +
                  `📊 P/L: ${tradeData.profit_loss}\n` +
                  `${tradeData.description || ''}\n\n` +
                  `#DeepRug #Trading #Crypto ${tradeData.tags || ''}`,
            mediaPath: memeImage
        };

        // 首先发布Meme图片
        const memeResults = await this.postContent(content);

        // 如果有认罪语音，作为单独的内容发布
        if (confessionVoice) {
            const voiceContent = {
                text: `🎤 Trader's Confession 😅\n` +
                      `Listen to what happened with ${tradeData.symbol} 🔊\n` +
                      `#TraderConfession #CryptoLife`,
                mediaPath: confessionVoice
            };
            const voiceResults = await this.postContent(voiceContent);
            return [...memeResults, ...voiceResults];
        }

        return memeResults;
    }

    async createThread(content, platforms = ['discord']) {
        const results = [];
        for (const platform of platforms) {
            if (platform === 'discord' && this.platforms[platform]) {
                try {
                    const result = await this.platforms[platform]({
                        ...content,
                        createThread: true
                    });
                    results.push({ platform, success: true, result });
                } catch (error) {
                    console.error(`Error creating thread on ${platform}:`, error);
                    results.push({ platform, success: false, error: error.message });
                }
            }
        }
        return results;
    }
}

module.exports = SocialMediaService;