/* -*- mode: C; c-basic-offset: 4; indent-tabs-mode: nil; -*- */
/* vim:set et sts=4:
 * IBus Input Engine Description Implementation
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

#ifdef HAVE_CONFIG_H
#  include "config.h"
#endif

#include "ibus-input-engine-desc.h"

#include <string.h>
#include <stdlib.h>

#define MY_ENGINE_DESC_GET_PRIVATE(o)   \
    ((IBusEngineDescPrivate *)ibus_engine_desc_get_instance_private ((o)))

/* Private structure */
struct _IBusEngineDescPrivate {
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

static guint MY_TYPE_ENGINE_DESC = 0;

G_DEFINE_TYPE_WITH_PRIVATE (IBusEngineDesc,
                            ibus_engine_desc,
                            IBUS_TYPE_OBJECT)

GType
ibus_engine_desc_get_type (void)
{
    return MY_TYPE_ENGINE_DESC;
}

/* Create new engine description */
IBusEngineDesc *
ibus_engine_desc_new (const gchar *name,
                      const gchar *author,
                      const gchar *author_email,
                      const gchar *icon,
                      const gchar *description,
                      const gchar *license,
                      gchar **lang,
                      const gchar *version)
{
    IBusEngineDesc *desc;
    
    desc = g_object_new (MY_TYPE_ENGINE_DESC,
                         "name", name,
                         "author", author,
                         "author-email", author_email,
                         "icon", icon,
                         "description", description,
                         "license", license,
                         "lang", lang,
                         "version", version,
                         NULL);
    
    return desc;
}

/* Get name */
const gchar *
ibus_engine_desc_get_name (IBusEngineDesc *desc)
{
    IBusEngineDescPrivate *priv = MY_ENGINE_DESC_GET_PRIVATE (desc);
    
    return priv->name ? priv->name : "";
}

/* Get author */
const gchar *
ibus_engine_desc_get_author (IBusEngineDesc *desc)
{
    IBusEngineDescPrivate *priv = MY_ENGINE_DESC_GET_PRIVATE (desc);
    
    return priv->author ? priv->author : "";
}

/* Get description */
const gchar *
ibus_engine_desc_get_description (IBusEngineDesc *desc)
{
    IBusEngineDescPrivate *priv = MY_ENGINE_DESC_GET_PRIVATE (desc);
    
    return priv->description ? priv->description : "";
}

/* Get languages */
gchar **
ibus_engine_desc_get_lang (IBusEngineDesc *desc)
{
    IBusEngineDescPrivate *priv = MY_ENGINE_DESC_GET_PRIVATE (desc);
    
    return priv->lang ? priv->lang : NULL;
}

/* Get version */
const gchar *
ibus_engine_desc_get_version (IBusEngineDesc *desc)
{
    IBusEngineDescPrivate *priv = MY_ENGINE_DESC_GET_PRIVATE (desc);
    
    return priv->version ? priv->version : "";
}

/* Class initialization */
static void
ibus_engine_desc_class_init (IBusEngineDescClass *klass)
{
    /* Class initialization code */
}

/* Instance initialization */
static void
ibus_engine_desc_init (IBusEngineDesc *desc)
{
    IBusEngineDescPrivate *priv = MY_ENGINE_DESC_GET_PRIVATE (desc);
    
    /* Initialize private members */
    priv->name = NULL;
    priv->author = NULL;
    priv->author_email = NULL;
    priv->icon = NULL;
    priv->description = NULL;
    priv->license = NULL;
    priv->lang = NULL;
    priv->property = NULL;
    priv->version = NULL;
}

/* Destroy function */
static void
ibus_engine_desc_destroy (IBusObject *object)
{
    IBusEngineDesc *desc = IBUS_ENGINE_DESC (object);
    IBusEngineDescPrivate *priv = MY_ENGINE_DESC_GET_PRIVATE (desc);
    
    g_free (priv->name);
    g_free (priv->author);
    g_free (priv->author_email);
    g_free (priv->icon);
    g_free (priv->description);
    g_free (priv->license);
    g_free (priv->version);
    
    g_strfreev (priv->lang);
    g_strfreev (priv->property);
    
    g_free (priv);
    g_object_unref (object);
}

/* IBusEngineDesc implementation */
IBusEngineDesc *
ibus_engine_desc_new (const gchar *name,
                      const gchar *author,
                      const gchar *author_email,
                      const gchar *icon,
                      const gchar *description,
                      const gchar *license,
                      gchar **lang,
                      const gchar *version)
{
    IBusEngineDesc *desc;
    
    desc = g_object_new (MY_TYPE_ENGINE_DESC,
                         "name", name,
                         "author", author,
                         "author-email", author_email,
                         "icon", icon,
                         "description", description,
                         "license", license,
                         "lang", lang,
                         "version", version,
                         NULL);
    
    return desc;
}
