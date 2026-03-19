/* -*- mode: C; c-basic-offset: 4; indent-tabs-mode: nil; -*- */
/* vim:set et sts=4:
 * IBus Input Engine Implementation
 * Copyright (C) 2026 Tars AI Assistant
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 */

#if !defined (__IBUS_H_INSIDE__) && !defined (IBUS_COMPILATION)
#error "Only <ibus.h> can be included directly"
#endif

#ifndef __IBUS_INPUT_ENGINE_H__
#define __IBUS_INPUT_ENGINE_H__

#include "ibus.h"
#include "ibusenginesimple.h"

G_BEGIN_DECLS

#define MY_TYPE_INPUT_ENGINE             \
    (my_input_engine_get_type ())
#define MY_INPUT_ENGINE(obj)             \
    (MY_TYPE_INPUT_ENGINE (obj))
#define MY_INPUT_ENGINE_CLASS(klass)     \
    (MY_TYPE_INPUT_ENGINE_CLASS (klass))
#define MY_IS_INPUT_ENGINE(obj)          \
    (MY_TYPE_INPUT_ENGINE (obj))
#define MY_INPUT_ENGINE_GET_CLASS(obj)   \
    (MY_TYPE_INPUT_ENGINE_CLASS (obj))

typedef struct _MyInputEngine MyInputEngine;
typedef struct _MyInputEngineClass MyInputEngineClass;
typedef struct _MyInputEnginePrivate MyInputEnginePrivate;

struct _MyInputEngine {
    IBusEngineSimple parent;
};

struct _MyInputEngineClass {
    IBusEngineSimpleClass parent;
};

struct _MyInputEnginePrivate {
    guint32              *key_history;
    gint                 key_history_len;
    gint                 key_history_max;
    char                 *preedit_text;
    guint                preedit_len;
    gboolean             preedit_visible;
    IBusText            *current_text;
    guint                current_text_len;
    guint                cursor_pos;
    guint                anchor_pos;
    guint32              last_keyval;
    guint32              last_keycode;
    guint32              last_state;
    gboolean             engine_enabled;
    gboolean             has_focus;
};

GType          my_input_engine_get_type       (void);

void           my_input_engine_init           (MyInputEngine           *engine);
void           my_input_engine_class_init     (MyInputEngineClass      *klass);
static void    my_input_engine_destroy        (IBusEngineSimple       *simple);
static void    my_input_engine_focus_in       (IBusEngine             *engine);
static void    my_input_engine_focus_out      (IBusEngine             *engine);
static void    my_input_engine_focus_in_id    (IBusEngine             *engine,
                                                const gchar            *object_path,
                                                const gchar            *client);
static void    my_input_engine_focus_out_id   (IBusEngine             *engine,
                                                const gchar            *object_path);
static void    my_input_engine_reset          (IBusEngine             *engine);
static gboolean my_input_engine_process_key_event
                                                (IBusEngine             *engine,
                                                 guint                  keyval,
                                                 guint                  keycode,
                                                 guint                  state);
static void    my_input_engine_page_up        (IBusEngine             *engine);
static void    my_input_engine_page_down      (IBusEngine             *engine);
static void    my_input_engine_cursor_up      (IBusEngine             *engine);
static void    my_input_engine_cursor_down    (IBusEngine             *engine);
static void    my_input_engine_candidate_clicked
                                                (IBusEngine             *engine,
                                                 guint                  index,
                                                 guint                  button,
                                                 guint                  state);
static void    my_input_engine_commit_char    (MyInputEngine          *engine,
                                                gunichar                ch);
static void    my_input_engine_commit_str     (MyInputEngine          *engine,
                                                const char             *str);
static void    my_input_engine_update_preedit_text
                                                (MyInputEngine          *engine);
static void    my_input_engine_set_capabilities
                                                (IBusEngine             *engine,
                                                 guint                  caps);
static void    my_input_engine_set_cursor_location
                                                (IBusEngine             *engine,
                                                 gint                   x,
                                                 gint                   y,
                                                 gint                   w,
                                                 gint                   h);

G_END_DECLS

#endif /* __IBUS_INPUT_ENGINE_H__ */
