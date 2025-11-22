"use client";

import { useState, useRef, useEffect } from "react";
import {
  Box,
  Container,
  Flex,
  HStack,
  VStack,
  Input,
  IconButton,
  Text,
  Spinner,
  Tabs,
} from "@chakra-ui/react";

import {
  IoSendSharp,
  IoCheckmarkSharp,
  IoCheckmarkDone,
} from "react-icons/io5";

import { BsChatDots, BsListTask, BsCalendar3 } from "react-icons/bs";

type Message = {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
  status?: "sent" | "delivered" | "read";
};

export default function ChatbotApp() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Hello! I'm Duke, your personal HR assistant. How can I help you today?",
      sender: "bot",
      timestamp: new Date(),
      status: "read",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userText = inputValue;

    const newMessage: Message = {
      id: Date.now().toString(),
      text: userText,
      sender: "user",
      timestamp: new Date(),
      status: "sent",
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText }),
      });

      if (!res.ok) {
        throw new Error("Backend error");
      }

      const data = await res.json();

      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: data.reply,
        sender: "bot",
        timestamp: new Date(),
        status: "delivered",
      };

      setMessages((prev) => [...prev, botResponse]);
    } catch (err) {
      console.error(err);
      const errorMsg: Message = {
        id: (Date.now() + 2).toString(),
        text: "Sorry, I couldn't reach Duke. Please try again.",
        sender: "bot",
        timestamp: new Date(),
        status: "delivered",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Flex h="100vh" bg="gray.50">
      {/* Navigation Sidebar */}
      <Box
        w="80px"
        bg="white"
        borderRight="1px solid"
        borderColor="gray.200"
        py={4}
      >
        <VStack gap={6}>
          <Box fontSize="2xl" fontWeight="bold" color="teal.500" mb={4}>
            D
          </Box>
          <Tabs.Root defaultValue="chat" orientation="vertical">
            <Tabs.List>
              <Tabs.Trigger value="chat" asChild>
                <VStack
                  gap={1}
                  cursor="pointer"
                  p={3}
                  borderRadius="lg"
                  _hover={{ bg: "teal.50" }}
                  color="gray.600"
                  _selected={{ color: "teal.600", bg: "teal.50" }}
                >
                  <BsChatDots size={24} />
                  <Text fontSize="xs">Chat</Text>
                </VStack>
              </Tabs.Trigger>

              <Tabs.Trigger value="tasks" asChild>
                <VStack
                  gap={1}
                  cursor="pointer"
                  p={3}
                  borderRadius="lg"
                  _hover={{ bg: "teal.50" }}
                  color="gray.600"
                  _selected={{ color: "teal.600", bg: "teal.50" }}
                >
                  <BsListTask size={24} />
                  <Text fontSize="xs">Tasks</Text>
                </VStack>
              </Tabs.Trigger>

              <Tabs.Trigger value="schedule" asChild>
                <VStack
                  gap={1}
                  cursor="pointer"
                  p={3}
                  borderRadius="lg"
                  _hover={{ bg: "teal.50" }}
                  color="gray.600"
                  _selected={{ color: "teal.600", bg: "teal.50" }}
                >
                  <BsCalendar3 size={24} />
                  <Text fontSize="xs">Schedule</Text>
                </VStack>
              </Tabs.Trigger>
            </Tabs.List>

            <Tabs.Content value="chat" p={0}>
              {/* Chat content - main view */}
            </Tabs.Content>

            <Tabs.Content value="tasks">
              <Container>
                <Text>Tasks view coming soon...</Text>
              </Container>
            </Tabs.Content>

            <Tabs.Content value="schedule">
              <Container>
                <Text>Schedule view coming soon...</Text>
              </Container>
            </Tabs.Content>
          </Tabs.Root>
        </VStack>
      </Box>

      {/* Main Chat Area */}
      <Flex flex={1} direction="column" bg="gray.50">
        {/* Chat Header */}
        <Box bg="white" borderBottom="1px solid" borderColor="gray.200" p={4}>
          <HStack gap={3}>
            <VStack align="start" gap={0}>
              <Text fontWeight="bold" color="gray.700">
                Duke
              </Text>
              <Text fontSize="xs" color="teal.600">
                Online
              </Text>
            </VStack>
          </HStack>
        </Box>

        {/* Messages Area */}
        <Box flex={1} overflowY="auto" p={4}>
          <VStack gap={3} align="stretch">
            {messages.map((msg) => (
              <Flex
                key={msg.id}
                justify={msg.sender === "user" ? "flex-end" : "flex-start"}
              >
                <Box maxW="70%">
                  <Box
                    bg={msg.sender === "user" ? "teal.400" : "white"}
                    color={msg.sender === "user" ? "white" : "gray.700"}
                    px={4}
                    py={2}
                    borderRadius="lg"
                    boxShadow="sm"
                  >
                    <Text>{msg.text}</Text>
                  </Box>
                  <HStack
                    gap={1}
                    mt={1}
                    justify={msg.sender === "user" ? "flex-end" : "flex-start"}
                  >
                    <Text fontSize="xs" color="gray.500">
                      {formatTime(msg.timestamp)}
                    </Text>
                    {msg.sender === "user" && (
                      <Box color="teal.500">
                        {msg.status === "read" ? (
                          <IoCheckmarkDone size={14} />
                        ) : (
                          <IoCheckmarkSharp size={14} />
                        )}
                      </Box>
                    )}
                  </HStack>
                </Box>
              </Flex>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <Flex justify="flex-start">
                <Box maxW="70%">
                  <Box
                    bg="white"
                    color="gray.700"
                    px={4}
                    py={3}
                    borderRadius="lg"
                    boxShadow="sm"
                  >
                    <HStack gap={2}>
                      <Spinner size="sm" color="teal.500" />
                      <Text fontSize="sm" color="gray.500">
                        Duke is thinking...
                      </Text>
                    </HStack>
                  </Box>
                </Box>
              </Flex>
            )}

            <div ref={messagesEndRef} />
          </VStack>
        </Box>

        {/* Input Area */}
        <Box bg="white" borderTop="1px solid" borderColor="gray.200" p={4}>
          <HStack gap={2}>
            <Input
              placeholder="Type a message... (e.g., 'I'm sick! What shall I do?')"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter" && !isLoading) handleSend();
              }}
              bg="gray.50"
              border="none"
              _focus={{ bg: "gray.100" }}
              color="black"
              disabled={isLoading}
            />
            <IconButton
              aria-label="Send message"
              colorScheme="teal"
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading}
              isLoading={isLoading}
            >
              <IoSendSharp />
            </IconButton>
          </HStack>
        </Box>
      </Flex>
    </Flex>
  );
}
