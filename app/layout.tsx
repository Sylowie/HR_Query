import { Provider } from "@/components/ui/provider";
import { Flex, Box } from "@chakra-ui/react";

import "./globals.css";

export const metadata = {
  title: "Chatbot App",
  description: "Chatbot App using Next.js + Chakra UI + Python + Ollama 3.1",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html>
      <body>
        <Provider>
          <Flex direction="column" minH="100vh">
            <Box as="main" flex="1">
              {children}
            </Box>
          </Flex>
        </Provider>
      </body>
    </html>
  );
}
