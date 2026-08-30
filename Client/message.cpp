#include "message.h"

Message::Message(Sender sender, QString content, QString binding /*= ""*/)
    : m_sender(sender), m_content(content), m_binding(binding) {}

Message::Message() {}

Sender Message::get_sender() const { return this->m_sender; }

QString Message::get_content() const { return this->m_content; }

QString Message::get_binding() const { return this->m_binding; }
