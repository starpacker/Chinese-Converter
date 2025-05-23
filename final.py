import re
import torch
import jieba
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer


class EnhancedPinyinConverter:
    _model = None
    _tokenizer = None
    _streamer = None
    _context = ""  # 保存连续的中文上下文

    @classmethod
    def initialize_model(cls, model_path="/Users/a29301/Desktop/DeepSeek-R1-Distill-Qwen-1.5B"):
        if cls._model is None or cls._tokenizer is None:
            print("🚀 正在初始化智能转换引擎...")
            cls._tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )
            cls._model = AutoModelForCausalLM.from_pretrained(
                model_path,
                trust_remote_code=True,
                device_map="auto",
                torch_dtype=torch.bfloat16
            )

            cls._streamer = TextStreamer(cls._tokenizer, skip_prompt=True, skip_special_tokens=True)

            print("✅ 模型加载完成！")
        return cls._tokenizer, cls._model

    @classmethod
    def _build_prompt(cls, pinyin_str):
        return f"""[智能拼音转换系统]

任务说明：
将连续拼音字符串精准转换为符合语境的中文文本。要求：
1. 正确切分拼音片段(无空格分隔）
2. 精确进行音节切分(如"zhongguoren" → "zhong guo ren")
3. 准确处理多音字(如"行xíng/háng")
4. 保持语义连贯性

转换规则：
- 输入格式:纯字母字符串(如"woaini")
- 输出格式:完整词句
- 优先选择常用词组
- 保持原文长度一致
- 不需要任何多余的解释说明,只需要给出最终转换结果

示例:
输入: "zhongguoren"
输出: "中国人" 
输入: "yidongdianhua"
输出: "移动电话" 
输入: "xianzai"
输出: "现在" 
输入: "hangkong"
输出: "航空" 
输入: "nihaoshijie"
输出: "你好世界" 
输入: "guangdongshenzhen"
输出: "广东深圳"

上下文参考：
{cls._context.strip() if cls._context else "无"} 

待转换输入：
{pinyin_str}

[转换结果]
"""

    @classmethod
    def _generate_response(cls, pinyin_str):
        tokenizer, model = cls.initialize_model(model_path="D:/qwen_0.6b")

        generation_config = {
            "max_new_tokens": 128,  # 减少生成长度
            "temperature": 0.1,
            "top_p": 0.9,
            "repetition_penalty": 1.3,  # 增强重复惩罚
            "do_sample": True,
            "pad_token_id": tokenizer.eos_token_id,
            "no_repeat_ngram_size": 3  # 避免重复
        }

        prompt = cls._build_prompt(pinyin_str)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(**inputs,
                                    streamer=cls._streamer,
                                    **generation_config)

        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # return full_response
        return full_response.split("[转换结果]")[-1].strip()  # 关键修正点

    @staticmethod
    def _post_process(sentence):
        # 清除残留符号
        sentence = re.sub(r"^[：、]", "", sentence)
        # 确保以标点结尾
        if not re.search(r"[。！？]$", sentence):
            sentence += "。"
        return sentence

    @classmethod
    def convert(cls, pinyin_str):
        try:
            print(f"\n🔍 正在分析输入：{pinyin_str}")
            raw_response = cls._generate_response(pinyin_str)
            print("🎯 原始响应解析中...")

            # 直接使用处理后的响应
            final_output = cls._post_process(raw_response)
            # 将当前转换结果加入上下文
            if cls._context:
                cls._context += final_output
            else:
                cls._context = final_output
            # 控制上下文长度（保留不超过200字符）
            if len(cls._context) > 200:
                cls._context = cls._context[-200:]
            return final_output
        except Exception as e:
            print(f"⚠️ 转换异常：{str(e)}")
            return "服务暂时不可用，请稍后再试"
    @classmethod
    def clear_context(cls):
        cls._context = ""


def main():
    parser = argparse.ArgumentParser(description="智能拼音转换系统")
    parser.add_argument("input", nargs="?",default="tiandi", help="输入拼音字符串")
    args = parser.parse_args()

    print("\n=== 智能拼音转换系统 v2.2 ===")

    input_str = args.input if args.input else input("📝 请输入拼音字符串：")

    if not re.match(r"^[a-zA-Z]+$", input_str):
        print("❌ 输入包含非法字符！只接受纯字母")
        return

    print("\n⏳ 正在转换中，请稍候...")
    result = EnhancedPinyinConverter.convert(input_str)

    print("\n✅ 转换结果：")
    print("━" * 40)
    print(result)
    print("━" * 40)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 操作已取消")
    except Exception as e:
        print(f"❌ 系统错误：{str(e)}")
