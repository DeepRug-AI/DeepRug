import os
import random
from PIL import Image, ImageDraw, ImageFont
from transformers import pipeline

class MemeGenerator:
    def __init__(self):
        self.sentiment_analyzer = pipeline('sentiment-analysis')
        self.text_generator = pipeline('text-generation')
        self.templates_dir = os.path.join(os.path.dirname(__file__), 'meme_templates')
        self.fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        
    def analyze_trade_sentiment(self, trade_data):
        """分析交易数据情绪"""
        trade_text = f"Trade {trade_data['symbol']} at {trade_data['price']} with {trade_data['profit_loss']}"
        sentiment = self.sentiment_analyzer(trade_text)[0]
        return sentiment['label'], sentiment['score']
    
    def generate_meme_text(self, sentiment, trade_data):
        """根据交易情绪生成嘲讽文本"""
        prompt_templates = {
            'POSITIVE': [
                "When you make {profit} on {symbol} and others are still waiting for dips:",
                "Me watching my {symbol} position going to the moon:",
                "That moment when your {symbol} trade hits the target:"
            ],
            'NEGATIVE': [
                "When you thought {symbol} was going up but it dumps instead:",
                "Me watching my {symbol} position getting liquidated:",
                "That feeling when you FOMO into {symbol} at the top:"
            ]
        }
        
        templates = prompt_templates['POSITIVE'] if sentiment == 'POSITIVE' else prompt_templates['NEGATIVE']
        template = random.choice(templates)
        
        return template.format(
            symbol=trade_data['symbol'],
            profit=trade_data.get('profit_loss', '0')
        )
    
    def create_meme(self, text, template_name='default.jpg', style='classic'):
        """创建Meme图片
        Args:
            text: 要添加的文本
            template_name: 模板图片名称
            style: 文字样式 ('classic', 'modern', 'minimal', 'bold')
        Returns:
            生成的meme图片路径
        """
        try:
            # 加载模板图片
            template_path = os.path.join(self.templates_dir, template_name)
            image = Image.open(template_path)
            draw = ImageDraw.Draw(image)
            
            # 样式配置
            style_configs = {
                'classic': {
                    'font': 'impact.ttf',
                    'size_ratio': 0.1,
                    'stroke_width': 2,
                    'text_color': 'white',
                    'stroke_color': 'black'
                },
                'modern': {
                    'font': 'helvetica.ttf',
                    'size_ratio': 0.08,
                    'stroke_width': 0,
                    'text_color': 'white',
                    'shadow_offset': 3
                },
                'minimal': {
                    'font': 'arial.ttf',
                    'size_ratio': 0.07,
                    'stroke_width': 1,
                    'text_color': 'black',
                    'background': True
                },
                'bold': {
                    'font': 'futura.ttf',
                    'size_ratio': 0.12,
                    'stroke_width': 3,
                    'text_color': 'yellow',
                    'stroke_color': 'red'
                }
            }
            
            style_config = style_configs.get(style, style_configs['classic'])
            
            # 设置字体
            font_path = os.path.join(self.fonts_dir, style_config['font'])
            font_size = int(image.width * style_config['size_ratio'])
        font = ImageFont.truetype(font_path, font_size)
        
        # 创建绘图对象
        draw = ImageDraw.Draw(image)
        
        # 计算文本位置
        text_width = draw.textlength(text, font=font)
        x = (image.width - text_width) / 2
        y = image.height * 0.1  # 文本位置在顶部10%处
        
        # 绘制文本边框
        outline_size = int(font_size * 0.05)
        for adj in range(-outline_size, outline_size + 1):
            for opp in range(-outline_size, outline_size + 1):
                draw.text((x + adj, y + opp), text, font=font, fill='black')
        
        # 绘制主文本
        draw.text((x, y), text, font=font, fill='white')
        
        return image
    
    def generate_trade_meme(self, trade_data):
        """生成交易相关的Meme"""
        # 分析交易情绪
        sentiment, _ = self.analyze_trade_sentiment(trade_data)
        
        # 生成Meme文本
        meme_text = self.generate_meme_text(sentiment, trade_data)
        
        # 选择合适的模板
        template_name = 'bullish.jpg' if sentiment == 'POSITIVE' else 'bearish.jpg'
        
        # 创建Meme
        meme = self.create_meme(meme_text, template_name)
        
        return meme
    
    def save_meme(self, meme, output_path):
        """保存Meme图片"""
        meme.save(output_path, quality=95)
        return output_path