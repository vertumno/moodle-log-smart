"""Unit tests for Portuguese column name support in ColumnMapper.

Tests the fix for STORY-1.2 requirement:
"Support for multiple language variations (English/Portuguese)"
"""

import pytest
from moodlelogsmart.core.auto_detect.column_mapper import ColumnMapper, ColumnMapping


class TestPortugueseColumns:
    """Test Portuguese column name mapping."""

    def test_portuguese_column_names_from_user_csv(self):
        """Test actual Portuguese column names from user's CSV file.

        CSV file: logs_46101. 1 - Tecnologias Educacionais I_20260122-2326.csv
        Columns: Hora, Nome completo, Usuário afetado, Contexto do Evento,
                 Componente, Nome do evento, Descrição, Origem, endereço IP
        """
        # Actual columns from user's CSV
        csv_columns = [
            'Hora',
            'Nome completo',
            'Usuário afetado',
            'Contexto do Evento',
            'Componente',
            'Nome do evento',
            'Descrição',
            'Origem',
            'endereço IP',
        ]

        mapper = ColumnMapper()
        mapping = mapper.map_columns(csv_columns)

        # Verify all required columns are mapped
        assert mapping.time == 'Hora'
        assert mapping.user_full_name == 'Nome completo'
        assert mapping.event_name == 'Nome do evento'
        assert mapping.component == 'Componente'
        assert mapping.event_context == 'Contexto do Evento'
        assert mapping.description == 'Descrição'

        # Verify optional columns
        assert mapping.affected_user == 'Usuário afetado'
        assert mapping.origin == 'Origem'
        assert mapping.ip_address == 'endereço IP'

    def test_portuguese_alternative_names(self):
        """Test alternative Portuguese column names."""
        csv_columns = [
            'Horário',  # Alternative for 'Hora'
            'Nome',  # Alternative for 'Nome completo'
            'Evento',  # Alternative for 'Nome do evento'
            'Módulo',  # Alternative for 'Componente'
            'Contexto',  # Alternative for 'Contexto do Evento'
            'Detalhes',  # Alternative for 'Descrição'
        ]

        mapper = ColumnMapper()
        mapping = mapper.map_columns(csv_columns)

        assert mapping.time == 'Horário'
        assert mapping.user_full_name == 'Nome'
        assert mapping.event_name == 'Evento'
        assert mapping.component == 'Módulo'
        assert mapping.event_context == 'Contexto'
        assert mapping.description == 'Detalhes'

    def test_mixed_english_portuguese_columns(self):
        """Test CSV with mixed English and Portuguese columns."""
        csv_columns = [
            'Time',  # English
            'Nome completo',  # Portuguese
            'Event name',  # English
            'Componente',  # Portuguese
            'Context',  # English
            'Descrição',  # Portuguese
        ]

        mapper = ColumnMapper()
        mapping = mapper.map_columns(csv_columns)

        assert mapping.time == 'Time'
        assert mapping.user_full_name == 'Nome completo'
        assert mapping.event_name == 'Event name'
        assert mapping.component == 'Componente'
        assert mapping.event_context == 'Context'
        assert mapping.description == 'Descrição'

    def test_portuguese_case_insensitive(self):
        """Test case-insensitive matching for Portuguese columns."""
        csv_columns = [
            'hora',  # lowercase
            'NOME COMPLETO',  # uppercase
            'Usuário Afetado',  # mixed case
            'CONTEXTO DO EVENTO',  # uppercase
            'componente',  # lowercase
            'Nome Do Evento',  # mixed case
            'DESCRIÇÃO',  # uppercase
            'origem',  # lowercase
            'Endereço IP',  # mixed case
        ]

        mapper = ColumnMapper()
        mapping = mapper.map_columns(csv_columns)

        # Should map regardless of case
        assert mapping.time == 'hora'
        assert mapping.user_full_name == 'NOME COMPLETO'
        assert mapping.affected_user == 'Usuário Afetado'
        assert mapping.event_context == 'CONTEXTO DO EVENTO'
        assert mapping.component == 'componente'
        assert mapping.event_name == 'Nome Do Evento'
        assert mapping.description == 'DESCRIÇÃO'
        assert mapping.origin == 'origem'
        assert mapping.ip_address == 'Endereço IP'

    def test_error_message_includes_portuguese_aliases(self):
        """Test that error message shows Portuguese aliases."""
        # Missing required 'time' column
        csv_columns = [
            'Nome completo',
            'Nome do evento',
            'Componente',
            'Contexto do Evento',
            'Descrição',
        ]

        mapper = ColumnMapper()

        with pytest.raises(ValueError) as exc_info:
            mapper.map_columns(csv_columns)

        error_msg = str(exc_info.value)
        # Should mention both English and Portuguese aliases
        assert 'Time' in error_msg or 'Hora' in error_msg
        assert 'Coluna obrigatória não encontrada: time' in error_msg
