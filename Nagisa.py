"""Nagisa, an offline English math assistant for the TI-Nspire CX II Python app."""

import math


class ExpressionParser:
    def __init__(self, text, x_value=0.0, variable="x"):
        self.text = text
        self.index = 0
        self.x_value = x_value
        self.variable = variable.lower()

    def parse(self):
        value = self.parse_expression()
        self.skip_spaces()
        if self.index != len(self.text):
            raise ValueError("Unrecognized content in expression")
        if isinstance(value, complex) or math.isnan(value) or math.isinf(value):
            raise ValueError("Expression result is not a finite real number")
        return value

    def skip_spaces(self):
        while self.index < len(self.text) and self.text[self.index] == " ":
            self.index += 1

    def parse_expression(self):
        value = self.parse_term()
        while True:
            self.skip_spaces()
            if self.take("+"):
                value += self.parse_term()
            elif self.take("-"):
                value -= self.parse_term()
            else:
                return value

    def parse_term(self):
        value = self.parse_unary()
        while True:
            self.skip_spaces()
            if self.take("*"):
                value *= self.parse_unary()
            elif self.take("/"):
                divisor = self.parse_unary()
                if divisor == 0:
                    raise ZeroDivisionError("Cannot divide by zero")
                value /= divisor
            else:
                return value

    def parse_unary(self):
        self.skip_spaces()
        if self.take("+"):
            return self.parse_unary()
        if self.take("-"):
            return -self.parse_unary()
        return self.parse_power()

    def parse_power(self):
        value = self.parse_primary()
        self.skip_spaces()
        if self.take("^"):
            value = value ** self.parse_unary()
        return value

    def parse_primary(self):
        self.skip_spaces()
        if self.take("("):
            value = self.parse_expression()
            self.skip_spaces()
            if not self.take(")"):
                raise ValueError("Mismatched parentheses")
            return value

        if self.index < len(self.text) and (
            "a" <= self.text[self.index] <= "z"
            or "A" <= self.text[self.index] <= "Z"
        ):
            start = self.index
            while self.index < len(self.text) and (
                "a" <= self.text[self.index] <= "z"
                or "A" <= self.text[self.index] <= "Z"
            ):
                self.index += 1
            name = self.text[start:self.index].lower()
            if name == self.variable:
                return self.x_value
            if name == "pi":
                return math.pi
            if name == "e":
                return math.e
            self.skip_spaces()
            if not self.take("("):
                raise ValueError("Unknown variable or function")
            argument = self.parse_expression()
            self.skip_spaces()
            if not self.take(")"):
                raise ValueError("Mismatched function parentheses")
            functions = {
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "sqrt": math.sqrt,
                "ln": math.log,
                "log": math.log10,
                "exp": math.exp,
                "abs": abs,
            }
            if name not in functions:
                raise ValueError("Unsupported function")
            return functions[name](argument)

        start = self.index
        has_digit = False
        while self.index < len(self.text) and self.text[self.index].isdigit():
            self.index += 1
            has_digit = True
        if self.index < len(self.text) and self.text[self.index] == ".":
            self.index += 1
            while self.index < len(self.text) and self.text[self.index].isdigit():
                self.index += 1
                has_digit = True

        if not has_digit:
            raise ValueError("A number is required here")

        return float(self.text[start:self.index])

    def take(self, character):
        if self.index < len(self.text) and self.text[self.index] == character:
            self.index += 1
            return True
        return False


def clean_expression(text):
    replacements = (
        ("what is", ""),
        ("what's", ""),
        ("calculate", ""),
        ("compute", ""),
        ("please", ""),
        ("equals", ""),
        ("equal to", ""),
        ("?", ""),
        ("=", ""),
        (" ", ""),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def format_number(value):
    if value == int(value):
        return str(int(value))
    return str(value)


def has_prefix(text, prefix):
    return text[:len(prefix)] == prefix


def contains_term(text, term):
    start = 0
    while True:
        position = text.find(term, start)
        if position < 0:
            return False
        end = position + len(term)
        left_is_word = position > 0 and (
            ("a" <= text[position - 1] <= "z")
            or ("0" <= text[position - 1] <= "9")
        )
        right_is_word = end < len(text) and (
            ("a" <= text[end] <= "z")
            or ("0" <= text[end] <= "9")
        )
        if not left_is_word and not right_is_word:
            return True
        start = position + 1


def is_word_character(character):
    return (
        ("a" <= character <= "z")
        or ("A" <= character <= "Z")
        or ("0" <= character <= "9")
        or character == "_"
    )


def replace_word(text, word, replacement):
    result = ""
    start = 0
    while True:
        position = text.find(word, start)
        if position < 0:
            result += text[start:]
            return result
        end = position + len(word)
        left_boundary = position == 0 or not is_word_character(text[position - 1])
        right_boundary = end == len(text) or not is_word_character(text[end])
        if left_boundary and right_boundary:
            result += text[start:position] + replacement
            start = end
        else:
            result += text[start:end]
            start = end


def evaluate_expression(expression, x_value=0.0, variable="x"):
    return ExpressionParser(expression, x_value, variable).parse()


def format_compact(value):
    rounded = round(value, 6)
    if rounded == int(rounded):
        return str(int(rounded))
    return str(rounded)


def split_function_arguments(text):
    arguments = []
    depth = 0
    start = 0
    for index, character in enumerate(text):
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("Mismatched parentheses")
        elif character == "," and depth == 0:
            arguments.append(text[start:index].strip())
            start = index + 1
    if depth != 0:
        raise ValueError("Mismatched parentheses")
    arguments.append(text[start:].strip())
    if any(argument == "" for argument in arguments):
        raise ValueError("Missing function argument")
    return arguments


def calculus_function_reply(text):
    lowered = text.lower().strip()
    function_name = ""
    if has_prefix(lowered, "fnint("):
        function_name = "fnint"
    elif has_prefix(lowered, "fndiff("):
        function_name = "fndiff"
    else:
        return None

    opening = len(function_name)
    if not lowered.endswith(")"):
        return "Use fnInt(expression, lower, upper, variable) or fnDiff(expression, point, variable)."
    try:
        arguments = split_function_arguments(text[opening + 1:-1])
        expected_count = 4 if function_name == "fnint" else 3
        if len(arguments) != expected_count:
            raise ValueError("Wrong number of arguments")
        expression = arguments[0].replace(" ", "")
        variable = arguments[-1].strip().lower()
        if not variable or not (
            ("a" <= variable[0] <= "z") or ("A" <= variable[0] <= "Z")
        ):
            raise ValueError("Variable must be a letter")
        for character in variable:
            if not (("a" <= character <= "z") or ("A" <= character <= "Z")):
                raise ValueError("Variable must contain letters only")

        if function_name == "fndiff":
            point = evaluate_expression(arguments[1], variable=variable)
            step = 0.0001 * max(1.0, abs(point))
            left = evaluate_expression(expression, point - step, variable)
            right = evaluate_expression(expression, point + step, variable)
            result = (right - left) / (2.0 * step)
            return "Approximate derivative: " + format_compact(result)

        lower = evaluate_expression(arguments[1], variable=variable)
        upper = evaluate_expression(arguments[2], variable=variable)
        steps = 200
        width = (upper - lower) / steps
        total = evaluate_expression(expression, lower, variable)
        total += evaluate_expression(expression, upper, variable)
        for index in range(1, steps):
            point = lower + index * width
            multiplier = 4.0 if index % 2 == 1 else 2.0
            total += multiplier * evaluate_expression(expression, point, variable)
        result = total * width / 3.0
        return "Approximate integral: " + format_compact(result)
    except (ValueError, ZeroDivisionError, OverflowError):
        return (
            "Invalid calculus function. Use fnInt(x^2,0,5,x) or "
            "fnDiff(x^2,3,x)."
        )


def calculus_reply(lowered, original):
    derivative_prefixes = ("differentiate ", "derivative of ", "derivative ")
    integral_prefixes = ("integrate ", "integral of ", "integral ")

    for prefix in derivative_prefixes:
        if has_prefix(lowered, prefix):
            body = original[len(prefix):].strip()
            parts = body.lower().split(" at ")
            if len(parts) != 2:
                return "Use: derivative x^2 at 3"
            expression = normalize_spoken_expression(parts[0])
            point_text = parts[1].lower().replace("x=", "").replace(" ", "")
            try:
                point = float(point_text)
                step = 0.0001 * max(1.0, abs(point))
                left = evaluate_expression(expression, point - step)
                right = evaluate_expression(expression, point + step)
                result = (right - left) / (2.0 * step)
                return "Approximate derivative at x=" + format_compact(point) + ": " + format_compact(result)
            except (ValueError, ZeroDivisionError, OverflowError):
                return "Could not evaluate that function. Check its syntax and domain."

    for prefix in integral_prefixes:
        if has_prefix(lowered, prefix):
            body = original[len(prefix):].strip()
            pieces = body.lower().split(" from ")
            if len(pieces) != 2:
                return "Use: integral x^2 from 0 to 3"
            bounds = pieces[1].split(" to ")
            if len(bounds) != 2:
                return "Use: integral x^2 from 0 to 3"
            expression = normalize_spoken_expression(pieces[0])
            try:
                start = float(bounds[0].strip())
                end = float(bounds[1].strip())
                steps = 200
                width = (end - start) / steps
                total = evaluate_expression(expression, start)
                total += evaluate_expression(expression, end)
                for index in range(1, steps):
                    point = start + index * width
                    multiplier = 4.0 if index % 2 == 1 else 2.0
                    total += multiplier * evaluate_expression(expression, point)
                result = total * width / 3.0
                return "Approximate integral: " + format_compact(result)
            except (ValueError, ZeroDivisionError, OverflowError):
                return "Could not evaluate that function. Check its syntax and domain."

    return None


def normalize_spoken_expression(text):
    expression = text.lower().strip().rstrip("?!,;.")
    for phrase in ("what is", "calculate", "compute", "evaluate", "please"):
        expression = expression.replace(phrase, " ")
    expression = expression.replace("to the power of", "^")
    expression = expression.replace("multiplied by", "*")
    expression = expression.replace("times", "*")
    expression = expression.replace("divided by", "/")
    expression = expression.replace("plus", "+")
    expression = expression.replace("minus", "-")
    expression = expression.replace("negative ", "-")
    expression = expression.replace("the ", "")
    expression = expression.strip()
    number_words = (
        ("zero", "0"), ("one", "1"), ("two", "2"), ("three", "3"),
        ("four", "4"), ("five", "5"), ("six", "6"), ("seven", "7"),
        ("eight", "8"), ("nine", "9"), ("ten", "10"),
    )
    for word, digit in number_words:
        expression = replace_word(expression, word, digit)
    expression = expression.replace("square root of ", "sqrt(")
    expression = expression.replace("percent of", "/100*")
    expression = expression.replace("percentage of", "/100*")
    if has_prefix(expression, "square of "):
        expression = expression[len("square of "):].strip() + "^2"
    elif has_prefix(expression, "cube of "):
        expression = expression[len("cube of "):].strip() + "^3"
    else:
        expression = expression.replace("squared", "^2")
        expression = expression.replace("cubed", "^3")
        expression = expression.replace(" square", "^2")
        expression = expression.replace(" cube", "^3")
    expression = expression.replace(" ", "")
    if has_prefix(expression, "sqrt(") and not expression.endswith(")"):
        expression += ")"
    expression = expression.rstrip("?!,;")
    if expression.endswith("."):
        expression = expression[:-1]
    return expression


def parse_number_at(text, index):
    while index < len(text) and text[index] == " ":
        index += 1
    start = index
    if index < len(text) and text[index] in "+-":
        index += 1
    digit_count = 0
    while index < len(text) and "0" <= text[index] <= "9":
        index += 1
        digit_count += 1
    if index < len(text) and text[index] == ".":
        index += 1
        while index < len(text) and "0" <= text[index] <= "9":
            index += 1
            digit_count += 1
    if digit_count == 0:
        return None
    return text[start:index], index


def find_interval_bounds(text):
    for index in range(len(text)):
        if text[index] not in "[(":
            continue
        first = parse_number_at(text, index + 1)
        if first is None:
            continue
        first_value, position = first
        while position < len(text) and text[position] == " ":
            position += 1
        if position >= len(text) or text[position] != ",":
            continue
        second = parse_number_at(text, position + 1)
        if second is None:
            continue
        second_value, position = second
        while position < len(text) and text[position] == " ":
            position += 1
        closing = ")" if text[index] == "(" else "]"
        if position < len(text) and text[position] == closing:
            return index, position + 1, first_value, second_value

    keywords = ("from", "between", "interval")
    positions = []
    for keyword in keywords:
        position = text.find(keyword)
        while position >= 0:
            before_ok = position == 0 or not is_word_character(text[position - 1])
            after = position + len(keyword)
            after_ok = after == len(text) or not is_word_character(text[after])
            if before_ok and after_ok:
                positions.append((position, keyword))
                break
            position = text.find(keyword, position + 1)
    positions.sort()

    for position, keyword in positions:
        cursor = position + len(keyword)
        while cursor < len(text) and text[cursor] == " ":
            cursor += 1
        if keyword == "interval" and text[cursor:cursor + 5] == "from ":
            cursor += 5
        first = parse_number_at(text, cursor)
        if first is None:
            continue
        first_value, cursor = first
        while cursor < len(text) and text[cursor] == " ":
            cursor += 1
        if text[cursor:cursor + 3] == "to ":
            cursor += 3
        elif text[cursor:cursor + 4] == "and ":
            cursor += 4
        elif cursor < len(text) and text[cursor] == ",":
            cursor += 1
        else:
            continue
        second = parse_number_at(text, cursor)
        if second is not None:
            second_value, end = second
            return position, end, first_value, second_value
    return None


def natural_calculus_reply(lowered, original):
    derivative_marker = None
    for marker in ("derivative of ", "differentiate ", "slope of "):
        position = lowered.find(marker)
        if position >= 0:
            derivative_marker = (position, marker)
            break
    if derivative_marker is not None:
        position, marker = derivative_marker
        body = original[position + len(marker):].strip()
        lowered_body = body.lower()
        at_position = lowered_body.find(" at ")
        if at_position < 0:
            return "Please include the point, for example: derivative of x squared at 3."
        expression = normalize_spoken_expression(body[:at_position])
        point_text = body[at_position + 4:].strip().replace("x=", "").replace("X=", "")
        point_text = normalize_spoken_expression(point_text)
        try:
            point = evaluate_expression(point_text)
            result = calculus_function_reply(
                "fnDiff(" + expression + "," + str(point) + ",x)"
            )
            return result or "I could not parse that derivative. Try: derivative of x squared at 3."
        except (ValueError, ZeroDivisionError, OverflowError):
            return "I could not parse that derivative. Try: derivative of x squared at 3."

    area_request = (
        "area under" in lowered
        or "area below" in lowered
        or "area beneath" in lowered
    )
    integral_request = (
        area_request
        or "integral" in lowered
        or "integrate " in lowered
        or "integrate(" in lowered
    )
    if not integral_request:
        return None

    bounds_match = find_interval_bounds(lowered)
    if bounds_match is None:
        return (
            "I can calculate area under a curve as a definite integral. "
            "Please give clear bounds, for example: area under x squared from 1 to 6."
        )

    bounds_start, _, lower_bound, upper_bound = bounds_match
    marker_positions = []
    for marker in ("area under ", "area below ", "area beneath ", "integral of ", "integrate "):
        position = lowered.find(marker)
        if position >= 0:
            marker_positions.append((position, marker))
    if not marker_positions:
        return None
    position, marker = min(marker_positions)
    start = position + len(marker)
    end = bounds_start
    expression_text = original[start:end].strip()
    for phrase in ("the curve", "curve", "the graph", "graph", "the function", "function"):
        expression_text = expression_text.replace(phrase, " ")
    expression_text = expression_text.replace("y = ", "").replace("y=", "")
    for phrase in ("in interval", "over interval", "on interval", "in", "over", "on"):
        if expression_text.endswith(phrase):
            expression_text = expression_text[:-len(phrase)]
            break
    expression = normalize_spoken_expression(expression_text)
    if expression == "":
        return "I could not identify the function. Try: area under x squared from 1 to 6."
    try:
        result = calculus_function_reply(
            "fnInt(" + expression + "," + lower_bound + "," + upper_bound + ",x)"
        )
        if result is None or result.startswith("Invalid calculus function"):
            return "I could not parse that function. Try a form such as: area under x squared from 1 to 6."
        return result
    except (ValueError, ZeroDivisionError, OverflowError):
        return "I could not parse that function. Try a form such as: area under x squared from 1 to 6."


def natural_calculation_reply(lowered, original):
    normalized = normalize_spoken_expression(original)
    allowed = "0123456789.+-*/^()"
    if not any(character.isdigit() for character in normalized):
        return None

    expression_candidate = normalized
    for function_name in ("sqrt", "sin", "cos", "tan", "ln", "log", "exp", "abs"):
        expression_candidate = expression_candidate.replace(function_name, "")
    if not all(character in allowed for character in expression_candidate):
        return None
    try:
        result = evaluate_expression(normalized)
        return "Answer: " + format_number(result)
    except (ValueError, ZeroDivisionError, OverflowError):
        return "I could not parse that calculation. Try saying, for example, five plus three."


def natural_statistics_reply(lowered, original):
    commands = (
        ("what is the standard deviation of ", "stdev"),
        ("standard deviation of ", "stdev"),
        ("what is the average of ", "average"),
        ("average of ", "average"),
        ("what is the mean of ", "mean"),
        ("mean of ", "mean"),
        ("what is the median of ", "median"),
        ("median of ", "median"),
        ("what is the mode of ", "mode"),
        ("mode of ", "mode"),
        ("what is the variance of ", "variance"),
        ("variance of ", "variance"),
    )
    for phrase, command in commands:
        if has_prefix(lowered.strip(), phrase):
            data = original.strip()[len(phrase):].strip().rstrip(" .?!")
            return statistics_reply(command + " " + data, command + " " + data)
    return None


def statistics_reply(lowered, original):
    commands = (
        ("standard deviation ", "standard deviation"),
        ("stdev ", "standard deviation"),
        ("variance ", "variance"),
        ("statistics ", "all"),
        ("stats ", "all"),
        ("mean ", "mean"),
        ("average ", "mean"),
        ("median ", "median"),
        ("mode ", "mode"),
    )
    selected = None
    prefix = ""
    for command, operation in commands:
        if has_prefix(lowered, command):
            selected = operation
            prefix = command
            break
    if selected is None:
        return None

    data_text = original[len(prefix):].strip()
    values = []
    if "," in data_text or ";" in data_text:
        data_text = data_text.replace(";", ",")
        items = data_text.split(",")
    else:
        items = data_text.split()
    try:
        for item in items:
            value = float(item.strip())
            if math.isnan(value) or math.isinf(value):
                return "Please enter finite real numbers only."
            values.append(value)
    except ValueError:
        return "Enter numbers separated by commas, for example: stats 2, 4, 4, 6"
    if not values:
        return "Enter at least one number."
    if len(values) > 100:
        return "Please enter no more than 100 numbers."

    count = len(values)
    total = sum(values)
    mean = total / count
    ordered = sorted(values)
    middle = count // 2
    if count % 2 == 1:
        median = ordered[middle]
    else:
        median = (ordered[middle - 1] + ordered[middle]) / 2.0

    frequencies = {}
    for value in values:
        frequencies[value] = frequencies.get(value, 0) + 1
    highest_frequency = max(frequencies.values())
    if highest_frequency == 1:
        modes = []
    else:
        modes = []
        for value in ordered:
            if frequencies[value] == highest_frequency and value not in modes:
                modes.append(value)

    squared_difference_sum = 0.0
    for value in values:
        difference = value - mean
        squared_difference_sum += difference * difference
    population_variance = squared_difference_sum / count
    sample_variance = None
    if count > 1:
        sample_variance = squared_difference_sum / (count - 1)

    if selected == "mean":
        return "Mean: " + format_compact(mean)
    if selected == "median":
        return "Median: " + format_compact(median)
    if selected == "mode":
        if not modes:
            return "Mode: no mode"
        return "Mode: " + ", ".join([format_compact(value) for value in modes])
    if selected == "variance":
        return "Population variance: " + format_compact(population_variance)
    if selected == "standard deviation":
        return "Population standard deviation: " + format_compact(math.sqrt(population_variance))

    mode_text = "none" if not modes else ", ".join([format_compact(value) for value in modes])
    result = (
        "Count: " + str(count)
        + "  Mean: " + format_compact(mean)
        + "  Median: " + format_compact(median)
        + "  Mode: " + mode_text
        + "\nMin: " + format_compact(ordered[0])
        + "  Max: " + format_compact(ordered[-1])
        + "  Range: " + format_compact(ordered[-1] - ordered[0])
        + "\nPopulation variance: " + format_compact(population_variance)
        + "  Population SD: " + format_compact(math.sqrt(population_variance))
    )
    if sample_variance is not None:
        result += (
            "\nSample variance: " + format_compact(sample_variance)
            + "  Sample SD: " + format_compact(math.sqrt(sample_variance))
        )
    return result


def concept_reply(lowered, state):
    if (
        "variance" in lowered
        and (
            lowered.strip() in ("variance", "population variance", "sample variance")
            or any(
                word in lowered
                for word in ("what", "explain", "meaning", "difference", "population", "sample")
            )
        )
    ):
        state.last_topic = "variance"
        return (
            "Variance measures how spread out data are around their mean. "
            "Find each deviation from the mean, square it, then average the squares.\n"
            "Population variance: sigma^2 = sum((x - mean)^2) / N. "
            "Sample variance: s^2 = sum((x - mean)^2) / (n - 1); "
            "the n - 1 correction helps estimate a population from a sample.\n"
            "Example: for 2, 4, 6, the mean is 4. Population variance = 8/3; "
            "sample variance = 4. A larger variance means more spread."
        )

    if "mean value theorem" in lowered or "mvt" in lowered:
        state.last_topic = "mvt"
        return (
            "Mean Value Theorem (MVT): if f is continuous on [a,b] and "
            "differentiable on (a,b), then some c in (a,b) satisfies "
            "f'(c) = (f(b)-f(a))/(b-a). The instantaneous slope at c equals "
            "the average slope across the interval.\n"
            "Example: f(x)=x^2 on [1,3] has average slope 4. Since f'(x)=2x, "
            "c=2 works."
        )

    if "intermediate value theorem" in lowered or "ivt" in lowered:
        state.last_topic = "ivt"
        return (
            "Intermediate Value Theorem (IVT): if f is continuous on [a,b], "
            "then it takes every value between f(a) and f(b) somewhere in "
            "[a,b]. In particular, if f(a) and f(b) have opposite signs, "
            "f has a root between them.\n"
            "Example: f(x)=x^2-2 is continuous on [1,2]; f(1)=-1 and f(2)=2, "
            "so it has a root between 1 and 2."
        )

    return None


def science_reply(lowered):
    if lowered.strip() in ("physics", "physics topics"):
        return (
            "Physics topics: Newton's laws, kinematics, energy, momentum, "
            "gravity, electricity, waves, density, pressure, and Hooke's law."
        )
    if lowered.strip() in ("chemistry", "chemistry topics"):
        return (
            "Chemistry topics: atoms, elements, ions, bonding, moles, "
            "concentration, conservation of mass, acids, bases, and pH."
        )
    if lowered.strip() in ("biology", "biology topics"):
        return (
            "Biology topics: cells, organelles, DNA, RNA, genetics, "
            "mitosis, meiosis, photosynthesis, respiration, and evolution."
        )

    entries = (
        (("newton's first law", "first law of motion", "law of inertia", "inertia"),
         "Newton's First Law (inertia): an object stays at rest or moves at constant velocity unless acted on by a net external force. Inertia is resistance to a change in motion."),
        (("newton's second law", "second law of motion", "force formula"),
         "Newton's Second Law: net force equals mass times acceleration, F = m*a. Force is measured in newtons (N), mass in kilograms (kg), and acceleration in m/s^2."),
        (("newton's third law", "third law of motion", "action and reaction"),
         "Newton's Third Law: when object A exerts a force on object B, B exerts an equal-magnitude, opposite-direction force on A. The forces act on different objects."),
        (("kinematics", "equations of motion", "constant acceleration"),
         "For constant acceleration: v = u + a*t; s = u*t + 0.5*a*t^2; v^2 = u^2 + 2*a*s. Here u is initial velocity, v final velocity, a acceleration, t time, and s displacement."),
        (("work energy theorem", "work-energy theorem"),
         "Work-Energy Theorem: net work equals the change in kinetic energy, W_net = delta KE. Kinetic energy is KE = 0.5*m*v^2. Work by a constant force parallel to displacement is W = F*d."),
        (("conservation of energy", "energy conservation"),
         "Conservation of Energy: energy is not created or destroyed; it changes form or moves between objects. In an isolated system, total energy remains constant."),
        (("momentum", "conservation of momentum"),
         "Momentum is p = m*v. In an isolated system with no net external force, total momentum is conserved. Impulse changes momentum: J = F*delta t = delta p for a constant force."),
        (("gravity", "universal gravitation", "gravitational force"),
         "Newton's Law of Universal Gravitation: F = G*m1*m2/r^2, where m1 and m2 are masses, r is the distance between their centers, and G is the gravitational constant."),
        (("ohm's law", "ohms law"),
         "Ohm's Law: V = I*R, where voltage V is measured in volts, current I in amperes, and resistance R in ohms. It applies to an ohmic component under suitable conditions."),
        (("electric power", "electrical power"),
         "Electric power is P = V*I. Using Ohm's Law, it can also be written P = I^2*R or P = V^2/R. Power is measured in watts (W)."),
        (("wave equation", "wave speed", "frequency and wavelength"),
         "Wave relation: wave speed equals frequency times wavelength, usually written v = f*lambda. Frequency is in hertz (Hz), wavelength in meters (m), and speed in m/s."),
        (("hooke's law", "hookes law", "spring force"),
         "Hooke's Law for an ideal spring: F = -k*x, where k is the spring constant and x is displacement from equilibrium. The minus sign means the restoring force points back toward equilibrium."),
        (("density",),
         "Density is mass per unit volume: rho = m/V. Common units include kg/m^3 and g/cm^3."),
        (("pressure",),
         "Pressure is force per unit area: P = F/A. Its SI unit is the pascal (Pa), equal to one newton per square meter."),
        (("chemical equation", "balancing equations", "balance equation"),
         "To balance a chemical equation, change coefficients (not subscripts) until each element has the same atom count on both sides. Example: 2H2 + O2 -> 2H2O."),
        (("ph scale", "what is ph", "what is the ph", "ph value", "acids and bases"),
         "The pH scale describes hydrogen-ion activity in aqueous solutions. Approximately, pH = -log10[H3O+] for dilute solutions. At 25 C, pH below 7 is acidic, 7 is neutral, and above 7 is basic."),
        (("atom", "atomic structure", "proton neutron electron"),
         "An atom has a nucleus containing protons and neutrons, with electrons around it. The proton number is the atomic number and identifies the element. A neutral atom has equal numbers of protons and electrons."),
        (("periodic table", "periodic law"),
         "The periodic table arranges elements by increasing atomic number. Elements in a column (group) often have similar chemical properties because they have related outer-electron structures."),
        (("ion", "ions"),
         "An ion is an atom or group of atoms with a net electric charge. Losing electrons makes a positive cation; gaining electrons makes a negative anion."),
        (("ionic bond", "ionic bonding"),
         "Ionic bonding is the electrostatic attraction between oppositely charged ions, often formed after electrons transfer from one atom to another. Many ionic compounds form extended crystal lattices."),
        (("covalent bond", "covalent bonding"),
         "A covalent bond forms when atoms share pairs of electrons. Covalent bonds commonly join nonmetal atoms in molecules."),
        (("mole", "avogadro constant", "avogadro's number"),
         "A mole is an amount containing exactly 6.02214076 x 10^23 specified entities. This number is the Avogadro constant. Entities may be atoms, molecules, ions, or other particles."),
        (("molarity", "molar concentration", "concentration formula"),
         "Molarity is amount of solute per volume of solution: c = n/V. It is commonly measured in mol/L. Use the final solution volume, not just the solvent volume."),
        (("solution", "solute and solvent", "homogeneous mixture"),
         "A chemical solution is a homogeneous mixture: the solute is distributed through the solvent. The amount of solute per volume of solution is its concentration."),
        (("conservation of mass", "law of conservation of mass"),
         "Conservation of Mass: in an ordinary chemical reaction, atoms are rearranged but not created or destroyed, so total mass is conserved in a closed system. A balanced equation has the same number of each atom on both sides."),
        (("neutralization", "acid base reaction"),
         "An acid-base neutralization commonly forms water and a salt. For example: HCl + NaOH -> NaCl + H2O. The exact products depend on the acid and base."),
        (("cell theory",),
         "Cell Theory: living organisms are made of one or more cells; the cell is the basic unit of life; and cells arise from pre-existing cells."),
        (("cell membrane", "plasma membrane"),
         "The cell membrane is a selectively permeable boundary. It helps regulate what enters and leaves the cell; its structure is mainly a phospholipid bilayer with proteins."),
        (("organelles", "cell organelles", "mitochondria", "mitochondrion"),
         "Organelles are specialized cell structures. The nucleus stores most eukaryotic DNA; mitochondria carry out much aerobic ATP production; ribosomes build proteins; chloroplasts perform photosynthesis in plants and algae."),
        (("photosynthesis",),
         "Photosynthesis stores light energy in chemical bonds. A simplified balanced equation is 6CO2 + 6H2O + light -> C6H12O6 + 6O2. In plants, it occurs mainly in chloroplasts."),
        (("cellular respiration", "aerobic respiration"),
         "Aerobic cellular respiration releases energy from glucose using oxygen. A simplified equation is C6H12O6 + 6O2 -> 6CO2 + 6H2O + usable energy (ATP)."),
        (("dna", "deoxyribonucleic acid"),
         "DNA stores hereditary information. It is usually a double helix with complementary base pairs: A pairs with T, and C pairs with G. A gene is a DNA sequence that contributes to a functional product."),
        (("rna", "ribonucleic acid"),
         "RNA is involved in gene expression and other cell processes. In RNA, uracil (U) is used instead of thymine (T). Messenger RNA carries a coding message; transfer RNA helps deliver amino acids during translation."),
        (("mitosis",),
         "Mitosis is nuclear division that usually produces two genetically similar daughter cells with the same chromosome number as the parent cell. It supports growth, repair, and asexual reproduction in some organisms."),
        (("meiosis",),
         "Meiosis is a two-stage cell division that produces haploid cells, usually four genetically varied products, from a diploid starting cell. It halves chromosome number and contributes to genetic variation."),
        (("natural selection", "evolution"),
         "Natural selection occurs when heritable traits affect survival or reproduction, causing trait frequencies to change across generations. Evolution is change in heritable population characteristics over generations."),
        (("enzyme", "enzymes"),
         "Enzymes are biological catalysts, usually proteins, that speed reactions by lowering activation energy. They are not consumed by the reaction; temperature, pH, and substrate can affect their activity."),
        (("homeostasis",),
         "Homeostasis is the regulation of internal conditions within a suitable range despite external changes. Feedback systems, often negative feedback, help maintain variables such as temperature or blood glucose."),
    )
    for keywords, explanation in entries:
        for keyword in keywords:
            if contains_term(lowered, keyword):
                return explanation
    return None


_SEMANTIC_EXAMPLES = (
    ("variance", "how spread out is a data set around its average"),
    ("variance", "what measures the average squared distance from the mean"),
    ("variance", "explain variability in a group of numbers"),
    ("mvt", "when does a tangent slope equal the average slope over an interval"),
    ("mvt", "which theorem says instantaneous rate can match average rate"),
    ("mvt", "what theorem relates derivative to secant slope"),
    ("ivt", "what theorem guarantees every value between two function outputs"),
    ("ivt", "when must a continuous graph cross the x axis"),
    ("ivt", "which theorem says a continuous function takes intermediate values"),
    ("newton's second law", "how are force mass and acceleration related"),
    ("newton's second law", "what law says net force equals mass times acceleration"),
    ("newton's second law", "calculate force using an object's mass and acceleration"),
    ("newton's first law", "what law says an object keeps moving unless a force acts"),
    ("newton's first law", "explain inertia and constant velocity"),
    ("newton's third law", "why do forces come in equal and opposite pairs"),
    ("conservation of energy", "what law says energy cannot be created or destroyed"),
    ("conservation of energy", "explain how energy changes form but total energy stays constant"),
    ("momentum", "what is mass times velocity and when is it conserved"),
    ("momentum", "explain impulse and change in motion"),
    ("gravity", "how do two masses attract each other"),
    ("gravity", "what is the formula for gravitational force"),
    ("ohm's law", "how are voltage current and resistance related"),
    ("ohm's law", "what electrical rule says voltage equals current times resistance"),
    ("electric power", "how do i calculate electrical power from voltage and current"),
    ("wave equation", "how are wave speed frequency and wavelength connected"),
    ("wave equation", "what is frequency multiplied by wavelength"),
    ("hooke's law", "how does a spring's restoring force depend on displacement"),
    ("kinematics", "which equations describe motion with constant acceleration"),
    ("density", "how much mass is packed into a given volume"),
    ("pressure", "what is force divided by area called"),
    ("chemical equation", "how do i balance atoms on both sides of a reaction"),
    ("chemical equation", "why can i change coefficients but not chemical subscripts"),
    ("atom", "what particles make up an atom and where are they"),
    ("periodic table", "how are chemical elements arranged by atomic number"),
    ("ion", "what do you call an atom that gains or loses electrons"),
    ("ionic bond", "what holds oppositely charged ions together"),
    ("covalent bond", "what kind of bond shares electron pairs"),
    ("mole", "how many particles are in one mole"),
    ("molarity", "how do you calculate moles of solute per liter of solution"),
    ("conservation of mass", "why is total mass unchanged in a chemical reaction"),
    ("ph scale", "what does acidity and alkalinity measure"),
    ("cell theory", "what are the basic ideas about cells and living organisms"),
    ("cell membrane", "what controls which substances enter and leave a cell"),
    ("organelles", "what do the nucleus mitochondria and ribosomes do"),
    ("photosynthesis", "how do plants turn light carbon dioxide and water into sugar"),
    ("photosynthesis", "what process stores sunlight as chemical energy in plants"),
    ("cellular respiration", "how do cells release usable energy from glucose"),
    ("cellular respiration", "how do cells use energy from glucose"),
    ("dna", "what molecule stores hereditary information"),
    ("dna", "what are the base pairing rules for genetic material"),
    ("rna", "which molecule uses uracil instead of thymine"),
    ("mitosis", "what cell division makes two similar daughter cells"),
    ("meiosis", "what cell division makes haploid cells and genetic variation"),
    ("natural selection", "how do inherited traits become more common over generations"),
    ("enzyme", "what biological catalyst lowers activation energy"),
    ("homeostasis", "how does the body keep internal conditions stable"),
)

_SEMANTIC_STOP_WORDS = (
    "a", "about", "an", "and", "are", "as", "at", "be", "been", "by",
    "can", "could", "do", "does", "f", "for", "from", "have", "how", "i",
    "if",
    "in", "is", "it", "of", "on", "or", "the", "to", "what", "when",
    "t", "this", "that", "where", "which", "why", "with", "x", "y",
)
_SEMANTIC_ALIASES = {
    "differentiate": "derivative",
    "differentiation": "derivative",
    "derivatives": "derivative",
    "derivative": "derivative",
    "integrate": "integral",
    "integration": "integral",
    "integrals": "integral",
    "integral": "integral",
    "accelerate": "acceleration",
    "accelerating": "acceleration",
    "accelerated": "acceleration",
    "accelerations": "acceleration",
    "acceleration": "acceleration",
    "velocity": "speed",
    "velocities": "speed",
    "speed": "speed",
    "force": "force",
    "forces": "force",
    "mass": "mass",
    "masses": "mass",
    "energy": "energy",
    "energies": "energy",
    "series": "series",
    "sequences": "sequence",
    "sequence": "sequence",
    "converges": "converge",
    "convergent": "converge",
    "convergence": "converge",
    "converge": "converge",
    "conserved": "conserve",
    "conserves": "conserve",
    "conserving": "conserve",
    "conservation": "conserve",
    "diverges": "diverge",
    "divergent": "diverge",
    "divergence": "diverge",
    "diverge": "diverge",
    "chemical": "chemistry",
    "chemistry": "chemistry",
    "chemicals": "chemistry",
    "physical": "physics",
    "physics": "physics",
    "biological": "biology",
    "biology": "biology",
    "organism": "organism",
    "organisms": "organism",
    "cell": "cell",
    "cells": "cell",
    "cellular": "cell",
    "use": "use",
    "uses": "use",
    "used": "use",
    "using": "use",
    "molecule": "molecule",
    "molecules": "molecule",
    "molecular": "molecule",
    "equations": "equation",
    "equation": "equation",
    "formulas": "formula",
    "formula": "formula",
    "theorems": "theorem",
    "theorem": "theorem",
    "explain": "explain",
    "explains": "explain",
    "explained": "explain",
    "explaining": "explain",
    "calculate": "calculate",
    "calculates": "calculate",
    "calculation": "calculate",
    "calculations": "calculate",
    "concentration": "molarity",
    "concentrations": "molarity",
    "solute": "molarity",
    "solutes": "molarity",
    "difficult": "difficult",
    "difficulty": "difficult",
    "hard": "difficult",
    "destroy": "destroy",
    "destroyed": "destroy",
    "creating": "create",
    "created": "create",
    "creation": "create",
    "tangent": "tangent",
    "tangents": "tangent",
    "slope": "slope",
    "slopes": "slope",
    "average": "average",
    "averages": "average",
    "accumulate": "accumulate",
    "accumulation": "accumulate",
    "accumulated": "accumulate",
    "accumulates": "accumulate",
    "continuous": "continuous",
    "continuity": "continuous",
    "continuously": "continuous",
    "between": "between",
    "intermediate": "between",
}
_SEMANTIC_MODEL = None


def _semantic_features(text):
    tokens = []
    current = ""
    for character in text.lower():
        if ("a" <= character <= "z") or ("0" <= character <= "9"):
            current += character
        elif current:
            if current not in _SEMANTIC_STOP_WORDS:
                tokens.append(_SEMANTIC_ALIASES.get(current, current))
            current = ""
    if current and current not in _SEMANTIC_STOP_WORDS:
        tokens.append(_SEMANTIC_ALIASES.get(current, current))

    features = {}
    for token in tokens:
        key = "w:" + token
        features[key] = features.get(key, 0) + 1
    for index in range(len(tokens) - 1):
        key = "b:" + tokens[index] + "_" + tokens[index + 1]
        features[key] = features.get(key, 0) + 1
    return features


def _build_semantic_model():
    document_features = []
    document_frequency = {}
    for target, example in _SEMANTIC_EXAMPLES:
        features = _semantic_features(example)
        document_features.append((target, features))
        for feature in features:
            document_frequency[feature] = document_frequency.get(feature, 0) + 1

    document_count = len(document_features)
    indexed_examples = []
    for target, features in document_features:
        vector = {}
        squared_norm = 0.0
        for feature, count in features.items():
            inverse_frequency = 1.0 + math.log(
                (document_count + 1.0) / (document_frequency[feature] + 1.0)
            )
            weight = count * inverse_frequency
            vector[feature] = weight
            squared_norm += weight * weight
        norm = math.sqrt(squared_norm)
        if norm > 0:
            for feature in vector:
                vector[feature] /= norm
        indexed_examples.append((target, vector))
    return indexed_examples, document_frequency, document_count


def semantic_knowledge_reply(lowered, state):
    global _SEMANTIC_MODEL
    if _SEMANTIC_MODEL is None:
        _SEMANTIC_MODEL = _build_semantic_model()

    examples, document_frequency, document_count = _SEMANTIC_MODEL
    features = _semantic_features(lowered)
    vector = {}
    squared_norm = 0.0
    for feature, count in features.items():
        frequency = document_frequency.get(feature)
        if frequency is None:
            continue
        inverse_frequency = 1.0 + math.log(
            (document_count + 1.0) / (frequency + 1.0)
        )
        weight = count * inverse_frequency
        vector[feature] = weight
        squared_norm += weight * weight
    if squared_norm == 0:
        return None

    norm = math.sqrt(squared_norm)
    for feature in vector:
        vector[feature] /= norm

    target_scores = {}
    for target, example_vector in examples:
        score = 0.0
        for feature, weight in vector.items():
            score += weight * example_vector.get(feature, 0.0)
        if score > target_scores.get(target, 0.0):
            target_scores[target] = score

    ranked_targets = sorted(
        target_scores.items(), key=lambda item: item[1], reverse=True
    )
    if not ranked_targets:
        return None
    best_target, best_score = ranked_targets[0]
    second_score = ranked_targets[1][1] if len(ranked_targets) > 1 else 0.0
    if best_score < 0.38 or best_score - second_score < 0.08:
        return None
    result = concept_reply(best_target, state)
    if result is not None:
        return result
    return science_reply(best_target)


_GENERATION_CORPUS = (
    "A useful study plan includes short sessions and time to review.",
    "When a problem feels difficult, write down what is known and what must be found.",
    "A small example can reveal a pattern that is difficult to see in an abstract rule.",
    "In mathematics, definitions explain what objects mean and theorems explain what follows.",
    "A limit describes the value that a function approaches near an input.",
    "The derivative measures instantaneous change and gives the slope of a tangent line.",
    "The chain rule helps differentiate a function built from other functions.",
    "Implicit differentiation is useful when an equation does not define y explicitly.",
    "A definite integral accumulates signed change across an interval.",
    "The Fundamental Theorem of Calculus connects differentiation with integration.",
    "Substitution can simplify an integral by changing its variable.",
    "Integration by parts is useful for products of functions.",
    "A differential equation describes a relationship involving an unknown function and its derivatives.",
    "An initial condition selects one solution from a family of possible solutions.",
    "A Taylor polynomial approximates a function near a chosen center.",
    "The ratio test can determine whether many infinite series converge.",
    "A power series has a radius of convergence that describes where it works.",
    "Parametric equations describe a curve using a changing parameter.",
    "Polar coordinates describe points using distance and angle.",
    "The speed of a particle is the magnitude of its velocity.",
    "An integral can represent area, accumulated distance, or total change.",
    "A good solution explains why each step is valid, not just what the answer is.",
    "If two methods give different results, check the assumptions and arithmetic.",
    "Try separating a long question into smaller parts that can be answered in order.",
    "Newton's Second Law relates net force, mass, and acceleration.",
    "Momentum is the product of an object's mass and velocity.",
    "Kinetic energy depends on mass and the square of speed.",
    "Work transfers energy when a force causes displacement.",
    "Conservation of energy means energy changes form but the total remains constant in an isolated system.",
    "Wave speed is frequency multiplied by wavelength.",
    "Ohm's Law relates voltage, current, and resistance.",
    "Density compares mass with volume, while pressure compares force with area.",
    "Atoms contain protons, neutrons, and electrons.",
    "The number of protons in an atom identifies its element.",
    "A chemical equation is balanced when each type of atom appears equally on both sides.",
    "Molarity is the amount of dissolved substance per volume of solution.",
    "A mole is a counting unit for a very large number of particles.",
    "The pH scale describes how acidic or basic an aqueous solution is.",
    "A chemical reaction rearranges atoms into different substances.",
    "Cells are the basic structural units of living organisms.",
    "DNA stores inherited information, and RNA helps use that information.",
    "Enzymes speed up biological reactions by lowering activation energy.",
    "Photosynthesis converts light energy into chemical energy.",
    "Cellular respiration releases usable energy from nutrients.",
    "Homeostasis helps keep internal conditions within a suitable range.",
    "Learning takes practice, and asking a precise question can make the next step clearer.",
    "There may be several ways to approach an idea, so compare the methods before choosing.",
    "I can help explain a concept or check a calculation, but I should not invent facts.",
    "If I misunderstood the question, adding a detail or example can help me respond better.",
    "A short break can make it easier to return to a challenging task.",
    "Creative ideas often improve when you try a few different possibilities.",
    "A flexible plan gives you room to adjust when you learn something new.",
    "What part of the idea would you like to explore first?",
    "What have you tried so far, and where did you get stuck?",
    "Could you give me a small example so I can understand what you mean?",
    "We can take the problem one step at a time.",
    "That is an interesting direction; what detail matters most to you?",
    "I am not certain about that yet, but I can help reason through the information you provide.",
    "A concrete example can make an abstract explanation easier to follow.",
    "The answer depends on the conditions, so it helps to state the assumptions.",
    "Check whether the final result has the right units and sign.",
    "For an estimate, explain the method and how accurate the result needs to be.",
    "A theorem guarantees a result only when its conditions are satisfied.",
    "When a graph is continuous, it has no breaks or jumps on the interval.",
    "Statistics summarize data, but the choice of summary depends on the question.",
    "The mean is sensitive to extreme values, while the median is more resistant.",
)
_GENERATION_STOP_WORDS = (
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "can",
    "could", "do", "does", "for", "from", "has", "have", "how", "i",
    "in", "is", "it", "of", "on", "or", "that", "the", "this", "to",
    "was", "what", "when", "where", "which", "why", "with", "you",
)
_GENERATION_MODEL = None


def _generation_words(text):
    words = []
    current = ""
    lowered = text.lower()
    for index, character in enumerate(lowered):
        if ("a" <= character <= "z") or ("0" <= character <= "9"):
            current += character
        elif (
            character == "'"
            and current
            and index + 1 < len(lowered)
            and ("a" <= lowered[index + 1] <= "z")
        ):
            current += character
        elif current:
            words.append(current)
            current = ""
    if current:
        words.append(current)
    return words


def _build_generation_model():
    transitions = {}
    sentence_features = []
    document_frequency = {}
    for sentence_index, sentence in enumerate(_GENERATION_CORPUS):
        words = _generation_words(sentence)
        if not words:
            continue
        features = set(
            feature[2:]
            for feature in _semantic_features(sentence)
            if feature.startswith("w:")
        )
        sentence_features.append((words, features))
        for word in features:
            document_frequency[word] = document_frequency.get(word, 0) + 1
        padded = ["<s>", "<s>"] + words + ["</s>"]
        for index in range(2, len(padded)):
            context = (padded[index - 2], padded[index - 1])
            choices = transitions.get(context)
            if choices is None:
                choices = []
                transitions[context] = choices
            choices.append((padded[index], sentence_index))
    return transitions, sentence_features, document_frequency


def generated_reply(lowered, state):
    global _GENERATION_MODEL
    if _GENERATION_MODEL is None:
        _GENERATION_MODEL = _build_generation_model()
    transitions, sentence_features, document_frequency = _GENERATION_MODEL

    query_features = set(
        feature[2:]
        for feature in _semantic_features(lowered)
        if feature.startswith("w:") and feature[2:] not in _GENERATION_STOP_WORDS
    )
    scored_sentences = []
    for sentence_index, (words, features) in enumerate(sentence_features):
        score = 0.0
        for word in query_features:
            if word in features:
                score += 1.0 + math.log(
                    (len(sentence_features) + 1.0)
                    / (document_frequency.get(word, 0) + 1.0)
                )
        overlap = len(query_features.intersection(features))
        scored_sentences.append((score, overlap, sentence_index, words))

    scored_sentences.sort(key=lambda item: (item[1], item[0]), reverse=True)
    best_score = scored_sentences[0][0]
    best_overlap = max(item[1] for item in scored_sentences)
    if (
        best_score <= 0
        or (len(query_features) > 1 and best_overlap < 2)
        or (
            len(query_features) == 1
            and document_frequency.get(next(iter(query_features)), 0) > 3
        )
    ):
        return (
            "I may need more context to understand that. "
            "Could you give me an example or explain which part matters most?"
        )
    candidates = []
    for score, overlap, sentence_index, words in scored_sentences:
        if score < best_score * 0.8:
            break
        if overlap == best_overlap:
            candidates.append((sentence_index, words))
    seed = state.turn_count + len(lowered)
    for character in lowered:
        seed = (seed * 33 + ord(character)) % 2147483647
    seed = (seed * 1103515245 + 12345) % 2147483647
    _, words = candidates[seed % len(candidates)]
    allowed_sentences = set(
        sentence_index for sentence_index, _ in candidates
    )
    output = words[:min(3, len(words))]
    context = ("<s>", "<s>")
    for word in output:
        context = (context[1], word)

    for _ in range(max(0, 24 - len(output))):
        choices = transitions.get(context, ())
        choices = [
            word for word, sentence_index in choices
            if sentence_index in allowed_sentences
        ]
        if not choices:
            break
        seed = (seed * 1103515245 + 12345) % 2147483647
        next_word = choices[seed % len(choices)]
        if next_word == "</s>":
            break
        output.append(next_word)
        context = (context[1], next_word)

    response = " ".join(output)
    if response:
        response = response[0].upper() + response[1:]
    if response and response[-1] not in ".!?":
        response += "."
    return response


class ConversationState:
    def __init__(self):
        self.name = ""
        self.interest = ""
        self.last_reply = ""
        self.last_topic = ""
        self.turn_count = 0
        self.pending_chat = ""
        self.chat_mood = ""


def daily_chat_reply(lowered, state):
    if state.pending_chat == "day_check":
        positive = ("good", "great", "pretty good", "fine", "okay", "all right", "not bad")
        negative = ("bad", "rough", "hard", "tiring", "stressful", "not great", "awful")
        if any(word in lowered for word in positive):
            state.pending_chat = ""
            return "Glad to hear there was something good in your day. What was the best part?"
        if any(word in lowered for word in negative):
            state.pending_chat = "support"
            return "Sorry it has been a rough day. Do you want to talk about what made it difficult, or would you rather take your mind off it?"
        if len(lowered) > 2:
            state.pending_chat = ""
            return "Thanks for telling me. What stood out most about your day?"

    if any(phrase in lowered for phrase in ("how was your day", "how has your day been")):
        state.pending_chat = "day_check"
        return "I do not have days like a person, but I am here and ready to chat. How has your day been?"
    if any(phrase in lowered for phrase in ("what are you doing", "what are you up to")):
        return "I am right here chatting with you. What are you up to?"
    if any(phrase in lowered for phrase in ("what should we talk about", "what can we talk about", "lets talk", "let's talk")):
        return "We could talk about music, games, food, a place you would like to visit, or something that happened today. Which sounds good?"
    if any(phrase in lowered for phrase in ("ask me a question", "ask me something")):
        prompts = (
            "If you could instantly get better at one skill, what would you choose?",
            "What is a small thing that reliably makes your day better?",
            "If you had a free afternoon, how would you like to spend it?",
            "What is something you have been curious about lately?",
        )
        state.pending_chat = "question_prompt"
        return prompts[state.turn_count % len(prompts)]
    if any(phrase in lowered for phrase in ("i don't know", "i dont know", "not sure")):
        return "That is okay; we do not need to have a perfect answer. Want an easy topic: music, food, movies, games, or how your day went?"

    feeling_groups = (
        (("i feel sad", "i am sad", "i'm sad", "i feel down", "i feel low"),
         "sad", "I am sorry things feel heavy right now. Would you like to tell me what has been going on?"),
        (("i feel anxious", "i am anxious", "i'm anxious", "i feel nervous", "i am nervous", "i'm nervous"),
         "anxious", "That sounds uncomfortable. If you want, tell me what is making you feel nervous, and we can take it one step at a time."),
        (("i feel stressed", "i am stressed", "i'm stressed", "i feel overwhelmed", "i am overwhelmed"),
         "stressed", "It sounds like a lot is landing on you at once. What is the one thing taking up the most space in your mind?"),
        (("i feel lonely", "i am lonely", "i'm lonely"),
         "lonely", "I am sorry you are feeling lonely. I can stay and chat for a while. Is there someone you trust you might also reach out to?"),
        (("i feel angry", "i am angry", "i'm angry", "i am mad", "i'm mad"),
         "angry", "It sounds like something really got under your skin. Want to tell me what happened?"),
        (("i feel excited", "i am excited", "i'm excited", "i can't wait"),
         "excited", "That is exciting! What are you looking forward to most?"),
        (("i feel proud", "i am proud", "i'm proud"),
         "proud", "You deserve to recognize that. What did you do that you feel proud of?"),
        (("i feel confused", "i am confused", "i'm confused"),
         "confused", "That can be frustrating. What part feels unclear? We can break it into smaller pieces."),
        (("i feel tired", "i am tired", "i'm tired", "i feel exhausted"),
         "tired", "Sounds like you have been using a lot of energy. Would rest help, or do you want to talk about what is keeping you busy?"),
        (("i am bored", "i'm bored", "i feel bored", "i am feeling bored"),
         "bored", "Want a change of pace? We could discuss music or movies, or make up a silly story."),
        (("i feel happy", "i am happy", "i'm happy", "i feel great", "i feel amazing", "i am excited"),
         "happy", "I am glad to hear that! What has been the best part?"),
    )
    for phrases, mood, response in feeling_groups:
        if any(phrase in lowered for phrase in phrases):
            state.chat_mood = mood
            if mood == "bored":
                state.pending_chat = "activity_choice"
            elif mood in ("sad", "anxious", "stressed", "lonely", "angry"):
                state.pending_chat = "support"
            else:
                state.pending_chat = "followup"
            return response

    if any(phrase in lowered for phrase in ("i had a bad day", "today was awful", "today was rough")):
        state.pending_chat = "support"
        state.chat_mood = "sad"
        return "I am sorry today was rough. Do you want to tell me what happened, or would you prefer a distraction?"
    if any(phrase in lowered for phrase in ("i had a good day", "today was great", "today was amazing")):
        state.pending_chat = "followup"
        state.chat_mood = "happy"
        return "I am glad! What made today a good one?"
    if any(phrase in lowered for phrase in ("i have an exam", "i have a test", "i have an interview")):
        state.pending_chat = "support"
        state.chat_mood = "nervous"
        return "That can feel like a lot. Are you feeling prepared, or is there one part you are most worried about?"
    if any(phrase in lowered for phrase in ("i passed", "i got the job", "i got accepted", "i did it")):
        state.pending_chat = "followup"
        return "That is wonderful news - congratulations! How are you feeling about it?"
    if any(phrase in lowered for phrase in ("i failed", "i got rejected", "i messed up", "i made a mistake")):
        state.pending_chat = "support"
        return "That is disappointing, and it is okay to feel upset about it. Do you want to talk through what happened or think about what to do next?"

    if any(phrase in lowered for phrase in ("what music do you like", "what is your favorite music", "favorite song")):
        state.pending_chat = "recommendation"
        return "I do not listen to music myself, but I can talk about it. What kind of music do you enjoy?"
    if any(phrase in lowered for phrase in ("what is your favorite food", "what food do you like")):
        state.pending_chat = "recommendation"
        return "I do not eat, but I am curious about your favorites. What food would you happily eat again tomorrow?"
    if any(phrase in lowered for phrase in ("what is your favorite movie", "what movies do you like")):
        state.pending_chat = "recommendation"
        return "I do not watch movies, but I can chat about them. What kind of movie do you usually enjoy?"
    if any(phrase in lowered for phrase in ("do you play games", "what games do you play")):
        state.pending_chat = "recommendation"
        return "I cannot play games, but I can talk about them or suggest a small game idea. What games are you into?"
    if any(phrase in lowered for phrase in ("good night", "goodnight")):
        return "Good night! I hope you get some good rest. We can pick up the conversation next time."
    if any(phrase in lowered for phrase in ("good luck", "wish me luck")):
        return "Good luck! Take it one step at a time - you have got this."
    if any(phrase in lowered for phrase in ("i appreciate you", "you are helpful", "you're helpful", "you are awesome", "you're awesome")):
        return "That is kind of you to say. I am glad I could help. What shall we do next?"

    if state.pending_chat == "activity_choice":
        if any(word in lowered for word in ("math", "calculation", "problem")):
            state.pending_chat = ""
            state.last_topic = ""
            return "Tell me which math topic you would like to explore, or send a calculation."
        if any(word in lowered for word in ("music", "movie", "suggestion")):
            state.pending_chat = "recommendation"
            return "What kind of music or movies do you usually enjoy?"
        if "story" in lowered:
            state.pending_chat = ""
            return "A tiny dragon wanted to fly to the moon. It practiced every day, and eventually learned that the best part was not reaching the moon - it was discovering how far it could go."
        if any(word in lowered for word in ("chat", "talk")):
            state.pending_chat = ""
            return "Sure. What has been on your mind lately?"

    if state.pending_chat == "recommendation" and len(lowered) > 2:
        state.pending_chat = ""
        return "Nice choice. What do you like most about that style?"

    if state.pending_chat == "support" and len(lowered) > 2:
        if any(phrase in lowered for phrase in ("i don't want to talk", "i dont want to talk", "rather not")):
            state.pending_chat = ""
            return "Of course. We can switch topics. Want a joke, a fun fact, or a math topic?"
        if any(phrase in lowered for phrase in ("thanks", "thank you")):
            state.pending_chat = ""
            return "You are welcome. We can take it at your pace. Would a distraction help?"
        state.pending_chat = ""
        return "That sounds like a lot to deal with. What would feel most helpful right now: thinking through one next step, getting a distraction, or just talking?"

    if state.pending_chat in ("followup", "question_prompt") and len(lowered) > 2:
        pending_chat = state.pending_chat
        state.pending_chat = ""
        if pending_chat == "question_prompt":
            return "That sounds interesting. What got you interested in it?"
        if state.chat_mood == "happy":
            return "That sounds like a bright spot. What did you enjoy most about it?"
        return "Thanks for telling me more. What happened next?"
    return None


def has_unnegated_phrase(text, phrase):
    start = 0
    negations = ("no", "not", "never", "don't", "dont", "without")
    while True:
        position = text.find(phrase, start)
        if position < 0:
            return False
        prefix = text[max(0, position - 14):position]
        recent_words = prefix.split()[-3:]
        negated = any(word in negations for word in recent_words)
        if not negated:
            return True
        start = position + len(phrase)


def health_reply(lowered, state):
    urgent_phrases = (
        "chest pain",
        "difficulty breathing",
        "shortness of breath",
        "can't breathe",
        "cannot breathe",
        "trouble speaking",
        "one-sided weakness",
        "sudden weakness",
        "fainted",
        "passed out",
        "lost consciousness",
        "severe sudden headache",
    )
    if any(has_unnegated_phrase(lowered, phrase) for phrase in urgent_phrases):
        state.pending_chat = ""
        return (
            "Those symptoms may need urgent medical attention. Please tell a trusted adult "
            "or someone nearby now and contact your local emergency service. Do not stay alone. "
            "I cannot diagnose or assess emergencies."
        )

    self_harm_phrases = (
        "i want to hurt myself",
        "i might hurt myself",
        "i want to kill myself",
        "i am going to kill myself",
        "i plan to kill myself",
        "i want to die",
        "thinking about suicide",
        "suicidal",
    )
    if any(has_unnegated_phrase(lowered, phrase) for phrase in self_harm_phrases):
        state.pending_chat = ""
        return (
            "I am really sorry you are facing this. Please tell a trusted person nearby "
            "right now and stay with them. If you may act on these thoughts or are in "
            "immediate danger, contact your local emergency service or a crisis hotline now. "
            "You deserve real-time support; I am not a crisis service."
        )

    dizziness_phrases = (
        "dizzy",
        "dizziness",
        "lightheaded",
        "light-headed",
        "feel faint",
        "feeling faint",
        "vertigo",
    )
    if any(contains_term(lowered, phrase) for phrase in dizziness_phrases):
        state.pending_chat = "health_check"
        return (
            "Sorry you are feeling dizzy. Sit or lie down somewhere safe, rest, and sip "
            "water if you can. Avoid driving, climbing, or standing up quickly, and tell "
            "a trusted adult or someone nearby. If it is severe, keeps returning, gets "
            "worse, or does not improve, contact a healthcare professional. If you faint, "
            "have chest pain, trouble breathing, sudden weakness, or trouble speaking, "
            "seek emergency help now. I cannot diagnose the cause."
        )

    if any(contains_term(lowered, phrase) for phrase in ("fever", "high temperature")):
        return (
            "Sorry you are feeling unwell. Rest, drink fluids if you can, and let a trusted "
            "adult know. Consider contacting a healthcare professional, especially if the "
            "fever is high, persistent, worsening, or comes with severe symptoms. I cannot diagnose you."
        )
    if any(contains_term(lowered, phrase) for phrase in ("nausea", "nauseous", "vomiting", "threw up")):
        return (
            "That sounds unpleasant. Rest and take small sips of fluid if you can. Tell a "
            "trusted adult; seek medical advice if it is severe, persistent, or you cannot "
            "keep fluids down. I cannot diagnose the cause."
        )
    if any(contains_term(lowered, phrase) for phrase in ("headache", "migraine")):
        return (
            "Sorry your head hurts. Rest somewhere comfortable and drink water if you can. "
            "Tell a trusted adult if it is severe, unusual, persistent, or getting worse. "
            "A sudden extremely severe headache or one with weakness, confusion, or trouble "
            "speaking needs urgent medical help. I cannot diagnose the cause."
        )
    if any(contains_term(lowered, phrase) for phrase in ("stomachache", "stomach ache", "stomach pain")):
        return (
            "Sorry your stomach hurts. Rest and tell a trusted adult. If the pain is severe, "
            "worsening, persistent, or accompanied by repeated vomiting or fainting, seek "
            "medical advice promptly. I cannot diagnose the cause."
        )

    if state.pending_chat == "health_check" and any(
        phrase in lowered for phrase in ("i feel better", "feeling better", "it stopped", "still dizzy", "still feel dizzy")
    ):
        state.pending_chat = ""
        if "better" in lowered or "stopped" in lowered:
            return "I am glad it has improved. Take it easy, and let someone know if it returns or worsens."
        return "Please stay seated or lying somewhere safe and tell someone nearby. If it is not improving, is severe, or keeps returning, contact a healthcare professional."

    mood_concerns = (
        "i feel hopeless",
        "nothing matters",
        "i can't cope",
        "i cannot cope",
        "i feel worthless",
        "i feel depressed",
    )
    if any(phrase in lowered for phrase in mood_concerns):
        state.chat_mood = "distressed"
        state.pending_chat = "support"
        return (
            "I am sorry things feel so heavy. You do not have to handle this alone - please "
            "consider telling someone you trust, such as a family member, counselor, or "
            "health professional. If you might hurt yourself or are in immediate danger, "
            "contact local emergency help now. I can listen, but I cannot assess or diagnose mental health."
        )
    return None


def _reply(message, state):
    text = message.strip()
    lowered = text.lower()

    if not text:
        return "Type a question, or type help to see what I can do."
    health_result = health_reply(lowered, state)
    if health_result is not None:
        return health_result
    if (
        lowered == "help"
        or "what can you do" in lowered
        or "how do i use" in lowered
    ):
        return (
            "I can calculate with +, -, *, /, ^, and parentheses. Example: calculate (12+3)*2\n"
            "Calculus: fnDiff(x^2,3,x); fnInt(x^2,0,3,x).\n"
            "You can also ask: calculate the area under x squared from 1 to 6.\n"
            "Spoken arithmetic works too: what is five plus three? What is the mean of 2, 4, 6?\n"
            "Arguments: fnInt(expression,lower,upper,variable); fnDiff(expression,point,variable).\n"
            "Statistics: stats 2, 4, 4, 6; also mean, median, mode, variance, stdev.\n"
            "Ask: explain variance, MVT, or IVT.\n"
            "Study support: ask AP Calculus BC-style questions, or ask about physics and chemistry concepts.\n"
            "Science: type physics, chemistry, or biology for topic lists, or ask about a law or term.\n"
            "Chat: daily life, feelings, hobbies, music, movies, and follow-up questions.\n"
            "Open-ended chat uses Nagisa TinyLM, a small offline word-level trigram language model; it may ask for clarification instead of inventing facts.\n"
            "I can offer basic wellbeing suggestions, but I cannot diagnose or replace medical help.\n"
            "I can remember your name and interests during this session.\n"
            "Ask about the Pythagorean theorem or the quadratic formula. Type exit to quit."
        )

    model_question = lowered.strip(" ?.!").replace("'", "")
    if model_question in (
        "model",
        "about the model",
        "what model are you",
        "what kind of model are you",
        "what model do you use",
        "what kind of model do you use",
        "do you use an llm",
        "are you a large language model",
    ):
        return (
            "I use Nagisa TinyLM, a small offline word-level trigram language model "
            "built from text bundled in this program. It can produce limited "
            "topic-matched replies, but it is not a neural LLM and cannot freely "
            "answer arbitrary questions. It needs no internet or external model files."
        )

    concept_result = concept_reply(lowered, state)
    if concept_result is not None:
        return concept_result
    science_result = science_reply(lowered)
    if science_result is not None:
        return science_result

    calculus_result = calculus_function_reply(text)
    if calculus_result is not None:
        return calculus_result
    calculus_result = natural_calculus_reply(lowered, text)
    if calculus_result is not None:
        return calculus_result
    calculus_result = calculus_reply(lowered, text)
    if calculus_result is not None:
        return calculus_result
    statistics_result = statistics_reply(lowered, text)
    if statistics_result is not None:
        return statistics_result
    statistics_result = natural_statistics_reply(lowered, text)
    if statistics_result is not None:
        return statistics_result
    natural_result = natural_calculation_reply(lowered, text)
    if natural_result is not None:
        return natural_result

    name_prefixes = ("please call me ", "call me ", "my name is ")
    for prefix in name_prefixes:
        if has_prefix(lowered, prefix):
            name = text[len(prefix):].strip(" ,.!?")
            if name:
                state.name = name
                greeting = "Got it. I will call you " + name + " during this session."
                if "and you" in lowered:
                    greeting += " I am Nagisa, your offline math assistant. Nice to meet you!"
                return greeting
            return "What should I call you?"

    if any(phrase in lowered for phrase in ("what do i like", "do you remember what i like")):
        if state.interest:
            state.last_topic = ""
            return "You told me that you like " + state.interest + "."
        return "You have not told me what you like yet."
    if state.last_topic == "mood_check" and any(
        phrase in lowered
        for phrase in ("pretty good", "good", "great", "not so good", "okay", "all right")
    ):
        state.last_topic = ""
        return "Thanks for telling me. I hope things go well! You can tell me about anything on your mind."
    if (
        has_prefix(lowered, "i like ")
        or has_prefix(lowered, "i love ")
        or has_prefix(lowered, "my favorite is ")
    ):
        if has_prefix(lowered, "my favorite is "):
            prefix = "my favorite is "
        elif has_prefix(lowered, "i love "):
            prefix = "i love "
        else:
            prefix = "i like "
        interest = text[len(prefix):]
        for separator in (",", ".", "!", "?"):
            interest = interest.split(separator, 1)[0]
        interest = interest.strip()
        interest_lower = interest.lower()
        if interest and not (
            has_prefix(interest_lower, "what") or has_prefix(interest_lower, "not")
        ):
            state.interest = interest
            state.last_topic = "interest_origin"
            return "I will remember that you like " + interest + ". How did you get interested in it?"

    if any(phrase in lowered for phrase in ("what is my name", "do you remember me", "remember my name")):
        if state.name:
            return "You told me to call you " + state.name + "."
        return "You have not told me your name yet."
    if any(phrase in lowered for phrase in ("say that again", "repeat that", "what did you just say")):
        return state.last_reply or "We have not chatted yet."
    follow_up = lowered.strip(" ?.!") in (
        "why", "why is that", "why does that happen", "how so",
        "tell me more", "explain that", "explain more",
        "how does that work",
    )
    if follow_up:
        if state.last_topic == "variance":
            return "Variance uses squared deviations so positive and negative differences do not cancel. The sample formula divides by n-1 rather than n to correct the typical underestimate of population variability."
        if state.last_topic == "mvt":
            return "The MVT guarantees a point where the tangent slope matches the secant slope, but it does not tell you exactly where that point is. Continuity and differentiability are essential conditions."
        if state.last_topic == "ivt":
            return "Continuity means the graph has no breaks or jumps on the interval. A continuous graph moving from a negative value to a positive value must cross zero."
        if state.last_topic == "pythagorean":
            return "Let a and b be the legs of a right triangle, and c its hypotenuse. The theorem says a^2 + b^2 = c^2."
        if state.last_topic == "quadratic":
            return "The quadratic formula comes from completing the square. For ax^2 + bx + c = 0, x = (-b +/- sqrt(b^2 - 4ac)) / (2a)."
        if state.interest:
            return "You mentioned that you like " + state.interest + ". What would you like to know about it?"
        return "Which part would you like me to explain in more detail?"

    chat_result = daily_chat_reply(lowered, state)
    if chat_result is not None:
        return chat_result

    if any(phrase in lowered for phrase in ("what is your name", "who are you", "introduce yourself")):
        return "I am Nagisa, an offline math assistant. I use a tiny statistical text model rather than a neural large language model, and I can also chat and calculate without an internet connection."
    if any(phrase in lowered for phrase in ("how are you", "how have you been")):
        state.last_topic = "mood_check"
        return "Thanks for asking! I am running well and ready to chat or help with calculations. How are you today?"
    if any(phrase in lowered for phrase in ("what do you like", "what is your favorite", "your hobbies")):
        state.last_topic = "interest"
        return "I am best at numbers and problem solving! If I had a hobby, it would be helping explain things. What do you like?"
    if any(phrase in lowered for phrase in ("thank you", "thanks")):
        return "You are welcome! Is there anything else you would like to chat about or calculate?"
    if any(phrase in lowered for phrase in ("i am tired", "i'm tired", "i feel tired")):
        return "Sounds like it has been a long day. Maybe take a break. If you like, you can tell me what happened."
    if any(phrase in lowered for phrase in ("i am happy", "i'm happy", "i feel great")):
        return "That is great! What made you happy?"
    if any(phrase in lowered for phrase in ("i am sad", "i'm sad", "i feel down", "i feel sad")):
        state.last_topic = "feeling"
        return "I am sorry you are having a hard time. If you want, you can tell me about it. I am listening."
    if any(phrase in lowered for phrase in ("i am bored", "i'm bored", "feeling bored")):
        state.last_topic = "game_choice"
        return "Want to do something? Ask about a math topic, chat, or send me a calculation problem."
    if state.last_topic == "game_choice":
        if "math" in lowered or "calculation" in lowered:
            state.last_topic = "study_calculus"
            return "Sure. Ask me an AP Calculus BC question, such as one about limits, series, parametric equations, or integration."
        if "chat" in lowered or "talk" in lowered:
            state.last_topic = ""
            return "Sure! Has anything interesting happened to you lately?"
    if "why is the sky blue" in lowered or "why is sky blue" in lowered:
        state.last_topic = "sky"
        return "Sunlight contains many colors. Air molecules scatter blue light more than most other colors, so the sky looks blue."
    if "what is a black hole" in lowered or "what are black holes" in lowered:
        state.last_topic = "black_hole"
        return "A black hole is an object with gravity so strong that even light cannot escape. Scientists study its effects on nearby matter and light."
    if any(phrase in lowered for phrase in ("what is artificial intelligence", "what is ai")):
        state.last_topic = "ai"
        return "Artificial intelligence helps computers perform tasks that usually require human intelligence, such as recognizing images or understanding text."
    if any(phrase in lowered for phrase in ("tell me a joke", "tell a joke")):
        jokes = (
            "Why was the math book sad? It had too many problems!",
            "Why did the equal sign stay humble? It knew it was not less than or greater than anyone else.",
        )
        return jokes[state.turn_count % len(jokes)]
    if any(phrase in lowered for phrase in ("tell me a story", "tell a story")):
        return "A little robot was afraid of making mistakes. One day it solved a hard problem by checking each step carefully. It learned that careful work matters more than never making a mistake."
    if any(phrase in lowered for phrase in ("i am learning", "i'm learning", "i am studying", "i'm studying")):
        return "Learning something new takes patience. How is it going? You can also send me a problem you are working on."
    if "and you" in lowered or "what about you" in lowered:
        if state.last_topic == "mood_check":
            return "I do not have feelings like a person, but I am here and happy to keep chatting."
        return "I do not have a human life or feelings, but I can keep chatting with you."
    if "pythagorean theorem" in lowered:
        state.last_topic = "pythagorean"
        return "The Pythagorean theorem: in a right triangle, the hypotenuse squared equals the sum of the squares of the other two sides: c^2 = a^2 + b^2."
    if "quadratic formula" in lowered or "quadratic equation" in lowered:
        state.last_topic = "quadratic"
        return "For ax^2 + bx + c = 0 (a != 0), the solutions are x = (-b +/- sqrt(b^2 - 4ac)) / (2a)."
    if any(
        contains_term(lowered, word)
        for word in ("hello", "hi", "good morning", "good afternoon", "good evening")
    ):
        greeting = "Hello"
        if state.name:
            greeting += ", " + state.name
        state.last_topic = "mood_check"
        greetings = (
            greeting + "! Nice to chat with you. How is your day going?",
            greeting + "! Anything new happening today?",
            greeting + "! Would you like to chat or calculate something?",
        )
        return greetings[state.turn_count % len(greetings)]

    expression = clean_expression(lowered)
    allowed = "0123456789.+-*/^()"
    if any(character.isdigit() for character in expression) and all(
        character in allowed for character in expression
    ):
        if len(expression) > 80:
            return "That expression is too long. Please keep it under 80 characters."
        try:
            result = ExpressionParser(expression).parse()
            return "Answer: " + format_number(result)
        except ZeroDivisionError:
            return "Calculation error: division by zero."
        except (ValueError, OverflowError):
            return "Invalid expression. Please check the numbers and parentheses."

    if state.last_topic == "interest_origin":
        state.last_topic = ""
        return "It sounds like you really enjoy " + state.interest + ". What else are you interested in?"

    semantic_result = semantic_knowledge_reply(lowered, state)
    if semantic_result is not None:
        return semantic_result

    return generated_reply(lowered, state)


def reply(message, state=None):
    if state is None:
        state = ConversationState()
    state.turn_count += 1
    response = _reply(message, state)
    state.last_reply = response
    return response


def main():
    print("Nagisa is ready. Type main() to chat with Nagisa.")
    state = ConversationState()
    while True:
        try:
            message = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if message.strip().lower() in ("goodbye", "bye", "quit", "quit()", "exit"):
            print("Goodbye!")
            break
        print("Nagisa: " + reply(message, state))


if __name__ == "__main__":
    main()
