/**
 * Coze Skill: 电商客服话术优化
 * 功能：根据用户问题自动生成专业、高转化的客服回答
 * 版本：1.0.0
 */

const productCatalog = {
  "连衣裙": {
    "material": "重磅真丝",
    "occasion": "商务会议、晚宴、约会",
    "price": "¥899",
    "promotion": "今日下单享88折"
  },
  "衬衫": {
    "material": "纯棉",
    "occasion": "日常办公、休闲出行",
    "price": "¥299",
    "promotion": "两件立减50元"
  },
  "外套": {
    "material": "羊毛混纺",
    "occasion": "秋冬保暖、商务通勤",
    "price": "¥1299",
    "promotion": "限时优惠券¥100"
  }
};

const standardResponses = {
  "greeting": "您好！欢迎光临我们的店铺，我是AI客服助手。请问有什么可以帮您？",
  "farewell": "感谢您的咨询！如果还有其他问题，随时找我哦～祝您购物愉快！",
  "price_concern": "我理解您对价格的考虑。这款产品采用{material}材质，适合{occasion}场合，现在购买还享受{promotion}。很多客户反馈物超所值呢！",
  "size_concern": "关于尺码问题，建议您参考我们的尺码表（已发送）。如果您身高{height}cm，体重{weight}kg，通常建议选择{size}码。需要我帮您详细分析吗？",
  "delivery_time": "我们默认发货后3-5天送达，具体物流信息您可以在订单页面查看。加急订单可联系客服处理。"
};

/**
 * 主处理函数
 * @param {string} userMessage - 用户输入
 * @param {object} context - 对话上下文
 * @returns {string} 客服回答
 */
function processCustomerService(userMessage, context = {}) {
  // 1. 意图识别
  const intent = classifyIntent(userMessage);

  // 2. 根据意图生成回答
  let response = "";
  switch(intent) {
    case "product_inquiry":
      response = handleProductInquiry(userMessage);
      break;
    case "price_question":
      response = handlePriceQuestion(userMessage);
      break;
    case "size_question":
      response = handleSizeQuestion(userMessage);
      break;
    case "delivery_question":
      response = handleDeliveryQuestion(userMessage);
      break;
    case "promotion_question":
      response = handlePromotionQuestion(userMessage);
      break;
    default:
      response = handleGeneralQuestion(userMessage);
  }

  // 3. 添加转化话术（如果适用）
  if (shouldAddConversionScript(intent)) {
    response += "\n\n" + generateConversionScript(intent, context);
  }

  return response;
}

/**
 * 意图分类
 */
function classifyIntent(message) {
  const lowerMsg = message.toLowerCase();

  if (lowerMsg.includes("什么场合") || lowerMsg.includes("适合") || lowerMsg.includes("材质") || lowerMsg.includes("面料")) {
    return "product_inquiry";
  }
  if (lowerMsg.includes("多少钱") || lowerMsg.includes("价格") || lowerMsg.includes("贵") || lowerMsg.includes("便宜")) {
    return "price_question";
  }
  if (lowerMsg.includes("尺码") || lowerMsg.includes("大小") || lowerMsg.includes("尺寸") || lowerMsg.includes("S/M/L")) {
    return "size_question";
  }
  if (lowerMsg.includes("发货") || lowerMsg.includes("物流") || lowerMsg.includes("快递") || lowerMsg.includes("几天到")) {
    return "delivery_question";
  }
  if (lowerMsg.includes("优惠") || lowerMsg.includes("折扣") || lowerMsg.includes("活动") || lowerMsg.includes("促销")) {
    return "promotion_question";
  }

  return "general_question";
}

/**
 * 处理产品咨询
 */
function handleProductInquiry(message) {
  // 提取产品关键词
  const products = Object.keys(productCatalog);
  let matchedProduct = null;
  for (const product of products) {
    if (message.includes(product)) {
      matchedProduct = product;
      break;
    }
  }

  if (matchedProduct && productCatalog[matchedProduct]) {
    const info = productCatalog[matchedProduct];
    return `这款${matchedProduct}采用${info.material}材质，垂感很好，适合${info.occasion}等场合。`;
  }

  return "您想了解哪款产品的具体信息呢？我可以为您详细介绍材质、适用场景和搭配建议。";
}

/**
 * 处理价格问题
 */
function handlePriceQuestion(message) {
  const products = Object.keys(productCatalog);
  let matchedProduct = null;
  for (const product of products) {
    if (message.includes(product)) {
      matchedProduct = product;
      break;
    }
  }

  if (matchedProduct && productCatalog[matchedProduct]) {
    const info = productCatalog[matchedProduct];
    return `这款${matchedProduct}的价格是${info.price}，采用${info.material}材质，现在购买还享受${info.promotion}。`;
  }

  return "我们的产品价格根据材质和工艺有所不同，您对哪款产品感兴趣？我可以为您详细报价。";
}

/**
 * 处理尺码问题
 */
function handleSizeQuestion(message) {
  return "尺码问题确实很重要！建议您参考我们的尺码表（已发送），如果您提供身高体重，我可以为您推荐合适的尺码。另外，我们的产品支持7天无理由退换，您可以放心选购。";
}

/**
 * 处理物流问题
 */
function handleDeliveryQuestion(message) {
  return standardResponses.delivery_time;
}

/**
 * 处理促销问题
 */
function handlePromotionQuestion(message) {
  return "目前我们有多种优惠活动：新用户注册领券、满299减30、限时折扣等。您对哪类产品感兴趣？我可以为您匹配最适合的优惠。";
}

/**
 * 处理一般问题
 */
function handleGeneralQuestion(message) {
  return standardResponses.greeting + " 您是想了解产品信息、优惠活动还是其他问题呢？";
}

/**
 * 是否添加转化话术
 */
function shouldAddConversionScript(intent) {
  return ["product_inquiry", "price_question", "size_question"].includes(intent);
}

/**
 * 生成转化话术
 */
function generateConversionScript(intent, context) {
  const scripts = [
    "今天下单可享专属优惠，需要我为您锁定库存吗？",
    "这款产品很受欢迎，库存紧张，建议尽早下单哦～",
    "如果您现在下单，我可以为您申请额外的小礼品。",
    "很多客户搭配购买这款产品，需要我为您推荐搭配方案吗？"
  ];

  const randomIndex = Math.floor(Math.random() * scripts.length);
  return scripts[randomIndex];
}

// 导出函数供Coze平台调用
module.exports = { processCustomerService };