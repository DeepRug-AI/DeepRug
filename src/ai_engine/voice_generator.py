import os
import torch
import logging
from transformers import pipeline
from TTS.api import TTS

class VoiceGenerator:
    def __init__(self, config):
        self.config = config
        self.text_generator = pipeline('text-generation')
        self.tts = TTS(config.voice.tts.model, gpu=torch.cuda.is_available())
        self.languages = {
            'en': 'English',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ru': 'Russian'
        }
        
        # 设置日志记录
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def generate_confession_text(self, trade_data, language='en'):
        """根据交易数据生成认罪文本"""
        templates = {
            'en': [
                "I confess that I FOMOed into {symbol} at {price}. I should have done more research. 😔",
                "I admit that I leveraged too much on {symbol} and lost {loss}. I was too greedy. 😭",
                "I acknowledge my mistake of not setting stop losses on {symbol}. It was pure gambling. 🎰",
                "I got rekt on {symbol} because I followed some random influencer. Never again! 🤦",
                "My portfolio is down {loss} because I aped into {symbol}. I'm such a degen. 🦍"
            ],
            'zh': [
                "我承认我在{price}的价格追高了{symbol}。我应该做更多研究的。😔",
                "我承认我在{symbol}上使用了过高的杠杆，亏损了{loss}。我太贪心了。😭",
                "我承认我没有在{symbol}上设置止损。这完全是在赌博。🎰",
                "我因为跟随某个网红买入{symbol}结果被割了。以后再也不会这样了！🤦",
                "我的投资组合因为冲动买入{symbol}已经亏损{loss}了。我就是个韭菜。🦍"
            ],
            'ja': [
                "{symbol}を{price}で追いかけ買いしてしまいました。もっと調査すべきでした。😔",
                "{symbol}で過度なレバレッジを使い、{loss}を失いました。欲が深すぎました。😭",
                "{symbol}でストップロスを設定しませんでした。ただの賭け事でした。🎰",
                "インフルエンサーに従って{symbol}を買って失敗しました。もう二度としません！🤦",
                "{symbol}に飛び込んで{loss}損失しました。私は本当にバカでした。🦍"
            ]
        }
        
        template = torch.randint(0, len(templates[language]), (1,)).item()
        text = templates[language][template].format(
            symbol=trade_data['symbol'],
            price=trade_data.get('price', '0'),
            loss=trade_data.get('loss', '0')
        )
        return text
    
    def generate_voice(self, text, language='en', speaker_name="default", output_path=None, emotion="neutral"):
        """生成语音文件
        Args:
            text: 要转换的文本
            language: 语言代码 ('en', 'zh', 'ja', 'ko', 'ru')
            speaker_name: 说话人名称
            output_path: 输出文件路径
            emotion: 情感类型 ('neutral', 'sad', 'happy', 'angry', 'excited', 'depressed')
        Returns:
            生成的语音文件路径
        """
        try:
            # 根据情感调整语音参数
            emotion_params = {
                'neutral': {'speed': 1.0, 'pitch': 1.0, 'energy': 1.0},
                'sad': {'speed': 0.8, 'pitch': 0.8, 'energy': 0.7},
                'happy': {'speed': 1.2, 'pitch': 1.2, 'energy': 1.3},
                'angry': {'speed': 1.3, 'pitch': 1.4, 'energy': 1.5},
                'excited': {'speed': 1.4, 'pitch': 1.3, 'energy': 1.6},
                'depressed': {'speed': 0.7, 'pitch': 0.7, 'energy': 0.5}
            }
            
            params = emotion_params.get(emotion, emotion_params['neutral'])
            
            # 如果没有指定输出路径，使用临时文件
            if not output_path:
                output_path = os.path.join(
                    os.path.dirname(__file__),
                    'generated_voices',
                    f'confession_{language}_{emotion}_{speaker_name}_{hash(text)}.wav'
                )
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 生成语音
            self.tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_name=speaker_name,
                language=self.languages[language],
                speed=params['speed'],
                pitch=params['pitch'],
                energy=params['energy']
            )
            
            self.logger.info(f"Successfully generated voice file: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating voice: {str(e)}")
            raise e
    
    def generate_trade_confession(self, trade_data, language='en', speaker_name="default", emotion="sad"):
        """生成交易认罪语音"""
        # 生成认罪文本
        confession_text = self.generate_confession_text(trade_data, language)
        
        # 生成语音文件
        voice_path = self.generate_voice(
            confession_text,
            language,
            speaker_name,
            emotion=emotion
        )
        
        return {
            'text': confession_text,
            'voice_path': voice_path,
            'language': language,
            'emotion': emotion
        }