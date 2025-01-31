const aiSocialConfig = {
    // 语音生成配置
    voice: {
        // TTS模型配置
        tts: {
            model: "tts_models/multilingual/multi-dataset/your_tts",
            defaultSpeaker: "default",
            outputDir: "generated_voices"
        },
        // 语音模板配置
        templates: {
            confession: {
                en: [
                    "I confess that I FOMOed into {symbol} at {price}. I should have done more research.",
                    "I admit that I leveraged too much on {symbol} and lost {loss}. I was too greedy.",
                    "I acknowledge my mistake of not setting stop losses on {symbol}. It was pure gambling."
                ],
                zh: [
                    "我承认我在{price}的价格追高了{symbol}。我应该做更多研究的。",
                    "我承认我在{symbol}上使用了过高的杠杆，亏损了{loss}。我太贪心了。",
                    "我承认我没有在{symbol}上设置止损。这完全是在赌博。"
                ],
                ja: [
                    "{symbol}を{price}で追いかけ買いしてしまいました。もっと調査すべきでした。",
                    "{symbol}で過度なレバレッジを使い、{loss}を失いました。欲が深すぎました。",
                    "{symbol}でストップロスを設定しませんでした。ただの賭け事でした。"
                ]
            }
        }
    },
    
    // 社交媒体配置
    social: {
        // 发布平台配置
        platforms: {
            twitter: {
                enabled: true,
                apiVersion: "2.0",
                rateLimit: 300, // 5分钟内的请求限制
                mediaSupport: true
            },
            telegram: {
                enabled: true,
                mediaSupport: true,
                maxMessageLength: 4096
            },
            discord: {
                enabled: true,
                mediaSupport: true,
                maxFileSize: 8388608 // 8MB
            }
        },
        
        // 内容发布策略
        postingStrategy: {
            retryAttempts: 3,
            retryDelay: 1000, // 毫秒
            priorityOrder: ["twitter", "telegram", "discord"],
            batchSize: 5 // 批量发布数量
        },
        
        // 内容模板
        templates: {
            tradeAlert: "🚨 Trade Alert! {symbol}\nPrice: {price}\nPosition: {position}\nLeverage: {leverage}x",
            confession: "😅 Trading Confession\n{text}\n#tradingconfession #{symbol}",
            meme: "🎭 {symbol} Trading Meme\n{caption}\n#tradingmeme #{symbol}"
        }
    }
};

module.exports = aiSocialConfig;