import re
from typing import List, Dict, Any, Optional, Tuple

class ContextQuestionMapper:
    """
    Maps context blocks to questions based on introduction patterns in the document text.
    Identifies patterns like "responda as três próximas questões" to correctly link contexts.
    """
    
    @staticmethod
    def map_contexts_to_questions(text: str, questions: List[Dict], context_blocks: List[Dict]) -> List[Dict]:
        """
        Analyze text to find context introduction patterns and map questions correctly.
        
        Args:
            text: Full document text
            questions: List of questions
            context_blocks: List of context blocks
            
        Returns:
            Updated questions with correct context_id values
        """
        # Find context introduction patterns and their positions
        context_mappings = ContextQuestionMapper._find_context_patterns(text)
        
        # Find question positions in text
        question_positions = ContextQuestionMapper._find_question_positions(text, questions)
        
        # Map questions to contexts based on proximity and patterns
        updated_questions = ContextQuestionMapper._assign_contexts_to_questions(
            questions, context_mappings, question_positions, context_blocks
        )
        
        return updated_questions
    
    @staticmethod
    def _find_context_patterns(text: str) -> List[Dict]:
        """Find context introduction patterns in text"""
        patterns = [
            {
                'pattern': r'Após ler atentamente o texto a seguir, responda as (\w+) próximas questões',
                'question_count_map': {'três': 3, 'duas': 2, 'uma': 1, 'quatro': 4, 'cinco': 5}
            },
            {
                'pattern': r'Leia o texto a seguir para responder as (\w+) próximas questões',
                'question_count_map': {'três': 3, 'duas': 2, 'uma': 1, 'quatro': 4, 'cinco': 5}
            },
            {
                'pattern': r'LEIA O TEXTO A SEGUIR',
                'question_count': 1  # Default to 1 question, will analyze dynamically
            },
            {
                'pattern': r'Leia (?:a|o) (?:crônica|texto) e depois resolva as próximas questões',
                'question_count': None  # Analyze dynamically
            },
            {
                'pattern': r'Analise (?:a|o) (?:imagem|texto) (?:abaixo|a seguir)',
                'question_count': 1
            },
            {
                'pattern': r'Leia este texto',
                'question_count': 1
            }
        ]
        
        context_mappings = []
        
        for pattern_info in patterns:
            pattern = pattern_info['pattern']
            # Use IGNORECASE flag for case-insensitive matching
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                mapping = {
                    'position': match.start(),
                    'end_position': match.end(),
                    'pattern_text': match.group(),
                    'question_count': None
                }
                
                # Extract question count if captured in pattern
                if 'question_count_map' in pattern_info and match.groups():
                    count_word = match.group(1).lower()
                    mapping['question_count'] = pattern_info['question_count_map'].get(count_word)
                elif 'question_count' in pattern_info:
                    mapping['question_count'] = pattern_info['question_count']
                
                context_mappings.append(mapping)
        
        # Sort by position in text
        context_mappings.sort(key=lambda x: x['position'])
        
        return context_mappings
    
    @staticmethod
    def _find_question_positions(text: str, questions: List[Dict]) -> List[Dict]:
        """Find the position of each question in the text"""
        question_positions = []
        
        for i, question in enumerate(questions):
            question_text = question.get('question', '')
            if not question_text:
                continue
            
            # Try different search strategies
            position = -1
            
            # Strategy 1: Search for question number pattern
            question_number = question.get('number', i + 1)
            number_pattern = f"QUESTÃO {question_number:02d}"
            position = text.find(number_pattern)
            
            if position == -1:
                number_pattern = f"QUESTÃO {question_number}"
                position = text.find(number_pattern)
            
            # Strategy 2: Search for beginning of question text
            if position == -1:
                # Clean question text for searching (first 30 characters)
                clean_question = question_text[:30].strip()
                # Remove punctuation for better matching
                import re
                clean_question = re.sub(r'[^\w\s]', '', clean_question)
                position = text.find(clean_question)
            
            # Strategy 3: Search for key phrases in question
            if position == -1:
                words = question_text.split()[:5]  # First 5 words
                if len(words) >= 3:
                    search_phrase = ' '.join(words)
                    position = text.find(search_phrase)
            
            question_positions.append({
                'index': i,
                'position': position,
                'question': question,
                'number': question_number
            })
        
        # Sort by position in text (put unfound questions at end)
        question_positions.sort(key=lambda x: x['position'] if x['position'] != -1 else float('inf'))
        
        return question_positions
    
    @staticmethod
    def _assign_contexts_to_questions(questions: List[Dict], context_mappings: List[Dict], 
                                    question_positions: List[Dict], context_blocks: List[Dict]) -> List[Dict]:
        """Assign context_id to questions based on mappings and positions"""
        updated_questions = [q.copy() for q in questions]
        
        # Reset all context_id to None first
        for question in updated_questions:
            question['context_id'] = None
        
        # SPECIAL HANDLING: Image-related questions
        ContextQuestionMapper._handle_image_questions(updated_questions, context_blocks)
        
        # Dynamic pattern-based mapping using detected context patterns
        for i, context_mapping in enumerate(context_mappings):
            if i >= len(context_blocks):
                continue
                
            context_block = context_blocks[i]
            context_id = context_block["id"]
            
            # Get the question count for this context
            question_count = context_mapping.get('question_count')
            if question_count is None:
                # Analyze dynamically if not specified
                question_count = ContextQuestionMapper._analyze_dynamic_question_count(
                    context_mapping, context_mappings, question_positions
                )
            
            # Find the next questions after this context pattern
            context_position = context_mapping['position']
            questions_for_context = []
            
            for q_pos in question_positions:
                if q_pos['position'] > context_position:
                    questions_for_context.append(q_pos)
                    if len(questions_for_context) >= question_count:
                        break
            
            # Assign context_id to these questions
            for q_pos in questions_for_context:
                question_index = q_pos['index']
                if question_index < len(updated_questions):
                    updated_questions[question_index]['context_id'] = context_id
        
        # Fallback: use proximity-based mapping for unmapped questions
        for i, question in enumerate(updated_questions):
            if question.get('context_id') is None:
                # Try to find best context based on proximity
                question_pos = None
                for q_pos in question_positions:
                    if q_pos['index'] == i:
                        question_pos = q_pos
                        break
                
                if question_pos and question_pos['position'] != -1:
                    best_context = ContextQuestionMapper._find_closest_context_by_proximity(
                        question_pos['position'], context_blocks, context_mappings
                    )
                    if best_context is not None:
                        question['context_id'] = best_context
        
        return updated_questions
    
    @staticmethod
    def _find_closest_context_by_proximity(question_position: int, context_blocks: List[Dict], 
                                          context_mappings: List[Dict]) -> Optional[int]:
        """Find the closest context block to a question position using intelligent proximity"""
        min_distance = float('inf')
        best_context = None
        
        for i, mapping in enumerate(context_mappings):
            if i < len(context_blocks):
                context_position = mapping['position']
                
                # Prefer contexts that come BEFORE the question (more natural flow)
                if context_position < question_position:
                    distance = question_position - context_position
                    # Apply a bonus for contexts that come before (more natural)
                    adjusted_distance = distance * 0.8
                else:
                    # Contexts after questions are less preferred
                    distance = context_position - question_position
                    adjusted_distance = distance * 1.2
                
                if adjusted_distance < min_distance:
                    min_distance = adjusted_distance
                    best_context = context_blocks[i]["id"]
        
        return best_context
    
    @staticmethod
    def _analyze_dynamic_question_count(mapping: Dict, all_mappings: List[Dict], 
                                       question_positions: List[Dict]) -> int:
        """Analyze how many questions belong to a context when count is not specified"""
        current_pos = mapping['position']
        
        # Find next context introduction
        next_context_pos = None
        for next_mapping in all_mappings:
            if next_mapping['position'] > current_pos:
                next_context_pos = next_mapping['position']
                break
        
        # Count questions between current context and next context
        question_count = 0
        for q_pos in question_positions:
            if q_pos['position'] > current_pos:
                if next_context_pos is None or q_pos['position'] < next_context_pos:
                    question_count += 1
                else:
                    break
        
        # Default strategies based on pattern text
        pattern_text = mapping.get('pattern_text', '').lower()
        
        # If no questions found between contexts, use intelligent defaults
        if question_count == 0:
            if 'leia o texto a seguir' in pattern_text or 'analise' in pattern_text:
                question_count = 1  # Usually single question contexts
            elif 'próximas questões' in pattern_text:
                question_count = 2  # Default for unspecified "próximas questões"
            else:
                question_count = 1  # Safe default
        
        return max(1, question_count)  # At least 1 question
    
    @staticmethod
    def validate_context_mappings(questions: List[Dict], context_blocks: List[Dict]) -> Dict[str, Any]:
        """Validate the context mappings and return statistics"""
        stats = {
            'total_questions': len(questions),
            'questions_with_context': 0,
            'questions_without_context': 0,
            'context_distribution': {},
            'issues': []
        }
        
        for question in questions:
            context_id = question.get('context_id')
            if context_id is not None:
                stats['questions_with_context'] += 1
                if context_id not in stats['context_distribution']:
                    stats['context_distribution'][context_id] = 0
                stats['context_distribution'][context_id] += 1
                
                # Validate context_id is valid
                if context_id >= len(context_blocks):
                    stats['issues'].append(f"Question has invalid context_id: {context_id}")
            else:
                stats['questions_without_context'] += 1
        
        return stats
    
    @staticmethod
    def _handle_image_questions(questions: List[Dict], context_blocks: List[Dict]):
        """Handle special mapping for image-related questions"""
        # Find image context block
        image_context_id = None
        for context in context_blocks:
            if context.get('hasImage') and 'analise a imagem' in context.get('statement', '').lower():
                image_context_id = context.get('id')
                break
        
        if image_context_id is None:
            return  # No image context found
        
        # Find questions that reference image content
        image_question_patterns = [
            r'sobre o texto analisado acima',
            r'texto analisado acima',
            r'analisado acima',
            r'imagem\s+(acima|anterior)',
            r'favor.*não.*dexar',
            r'obigetos.*corredor'
        ]
        
        for question in questions:
            question_text = question.get('question', '').lower()
            
            # Check if question mentions image-related patterns
            for pattern in image_question_patterns:
                if re.search(pattern, question_text, re.IGNORECASE):
                    question['context_id'] = image_context_id
                    print(f"🖼️  DEBUG: Questão {question.get('number')} vinculada ao bloco de imagem (context_id {image_context_id})")
                    break
