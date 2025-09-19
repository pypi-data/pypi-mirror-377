import {
  ChatInstance,
  HistoryItem,
  MessageResponseTypes,
  TextItem,
} from "@carbon/ai-chat";

const HISTORY = [
  {
    message: {
      id: "1",
      input: {
        text: "text 1",
        message_type: "text",
      },
    },
    time: new Date().toISOString(),
  },
  {
    message: {
      id: "2",
      output: {
        generic: [
          {
            text: new Array(40).fill("words from history").join(" "),
            response_type: MessageResponseTypes.TEXT,
          } satisfies TextItem as TextItem,
        ],
      },
    },
    time: new Date().toISOString(),
  },
  {
    message: {
      id: "3",
      input: {
        text: "some more words from history",
        message_type: "text",
      },
    },
    time: new Date().toISOString(),
  },
  {
    message: {
      id: "4",
      output: {
        generic: [
          {
            text: new Array(100).fill("more words").join(" "),
            response_type: MessageResponseTypes.TEXT,
          } satisfies TextItem as TextItem,
        ],
      },
    },
    time: new Date().toISOString(),
  },
] as HistoryItem[];

async function sleep(milliseconds: number) {
  await new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}

async function customLoadHistory(instance: ChatInstance) {
  // Mocking a delay in loading.
  await sleep(3000);
  return HISTORY;
}

export { customLoadHistory };
