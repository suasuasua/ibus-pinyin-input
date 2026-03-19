/* -*- mode: C; c-basic-offset: 4; indent-tabs-mode: nil; -*- */
/* vim:set et sts=4:
 * IBus Input Engine Description
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

#ifndef __IBUS_INPUT_ENGINE_DESC_H__
#define __IBUS_INPUT_ENGINE_DESC_H__

#include "ibus.h"

G_BEGIN_DECLS

/**
 * IBusEngineDesc:
 *
 * Structure that describes an input method engine.
 */
struct _IBusEngineDesc {
    IBusObject parent;
    gchar *name;
    gchar *author;
    gchar *author_email;
    gchar *icon;
    gchar *description;
    gchar *license;
    gchar **lang;
    gchar **property;
    gchar *version;
};

/**
 * IBUS_TYPE_ENGINE_DESC:
 *
 * The type of IBusEngineDesc.
 */
#define IBUS_TYPE_ENGINE_DESC             \
    (ibus_engine_desc_get_type ())
#define IBUS_ENGINE_DESC(obj)             \
    (G_TYPE_CHECK_INSTANCE_CAST ((obj), IBUS_TYPE_ENGINE_DESC, IBusEngineDesc))
#define IBUS_ENGINE_DESC_CLASS(klass)     \
    (G_TYPE_CHECK_CLASS_CAST ((klass), IBUS_TYPE_ENGINE_DESC, IBusEngineDescClass))
#define IBUS_IS_ENGINE_DESC(obj)          \
    (G_TYPE_CHECK_INSTANCE_TYPE ((obj), IBUS_TYPE_ENGINE_DESC))
#define IBUS_IS_ENGINE_DESC_CLASS(klass)  \
    (G_TYPE_CHECK_CLASS_TYPE ((klass), IBUS_TYPE_ENGINE_DESC))
#define IBUS_ENGINE_DESC_GET_CLASS(obj)   \
    (G_TYPE_INSTANCE_GET_CLASS ((obj), IBUS_TYPE_ENGINE_DESC, IBusEngineDesc))

typedef struct _IBusEngineDesc IBusEngineDesc;
typedef struct _IBusEngineDescClass IBusEngineDescClass;

GType ibus_engine_desc_get_type (void);

/**
 * ibus_engine_desc_new:
 * @name: Name of the engine.
 * @author: Author name.
 * @author_email: Author email.
 * @icon: Icon filename.
 * @description: Description of the engine.
 * @license: License.
 * @lang: Supported languages (array of strings).
 * @version: Version string.
 *
 * Create a new IBusEngineDesc.
 *
 * Returns: A newly allocated IBusEngineDesc.
 */
IBusEngineDesc *
             ibus_engine_desc_new          (const gchar        *name,
                                             const gchar        *author,
                                             const gchar        *author_email,
                                             const gchar        *icon,
                                             const gchar        *description,
                                             const gchar        *license,
                                             gchar              **lang,
                                             const gchar        *version);

/**
 * ibus_engine_desc_get_name:
 * @desc: An IBusEngineDesc.
 *
 * Get the name of an IBusEngineDesc.
 *
 * Returns: The name of the engine.
 */
const gchar *
             ibus_engine_desc_get_name     (IBusEngineDesc     *desc);

/**
 * ibus_engine_desc_get_author:
 * @desc: An IBusEngineDesc.
 *
 * Get the author of an IBusEngineDesc.
 *
 * Returns: The author name.
 */
const gchar *
             ibus_engine_desc_get_author   (IBusEngineDesc     *desc);

/**
 * ibus_engine_desc_get_description:
 * @desc: An IBusEngineDesc.
 *
 * Get the description of an IBusEngineDesc.
 *
 * Returns: The description string.
 */
const gchar *
             ibus_engine_desc_get_description
                                            (IBusEngineDesc     *desc);

/**
 * ibus_engine_desc_get_lang:
 * @desc: An IBusEngineDesc.
 *
 * Get the supported languages of an IBusEngineDesc.
 *
 * Returns: Array of language strings.
 */
gchar **
             ibus_engine_desc_get_lang     (IBusEngineDesc     *desc);

/**
 * ibus_engine_desc_get_version:
 * @desc: An IBusEngineDesc.
 *
 * Get the version of an IBusEngineDesc.
 *
 * Returns: The version string.
 */
const gchar *
             ibus_engine_desc_get_version  (IBusEngineDesc     *desc);

G_END_DECLS

#endif /* __IBUS_INPUT_ENGINE_DESC_H__ */
