package org.kson.schema.validators

import org.kson.KsonNumber
import org.kson.parser.MessageSink
import org.kson.parser.messages.MessageType
import org.kson.schema.JsonNumberValidator

class MaximumValidator(private val maximum: Double) : JsonNumberValidator() {
    override fun validateNumber(node: KsonNumber, messageSink: MessageSink) {
        val number = node.value.asDouble
        if (number > maximum) {
            messageSink.error(node.location, MessageType.SCHEMA_VALUE_TOO_LARGE.create(maximum.toString()))
        }
    }
}
